#!/usr/bin/env node
/**
 * Put marks on a tldraw canvas, and look at what you did.
 *
 *   node cli.mjs <doc.json> --ops ops.json --png look.png [--scale 2]
 *
 * The document on disk is the drawing. Each call loads it, applies the
 * operations, saves it back, and renders a PNG -- so the drawing survives
 * between calls without anything having to stay running, and the same file
 * opens in tldraw for a human to edit by hand afterwards.
 *
 * TWO THINGS ABOUT THAT, BOTH PAID FOR:
 *
 * Ops are APPENDED. A flat script that is edited and re-run appends its whole
 * history again and the drawing DOUBLES on run 2 -- a handlebar drawn twice
 * 12px apart was diagnosed for rounds as a badly-drawn fist. For a
 * script-driven drawing the persistence is a hazard, not a feature: have
 * build.sh `rm -f DOC.json` before every call, so the document is rebuilt from
 * the one flat script every time and the script stays the single source of
 * truth. pen's fixed default seed makes the hand identical run to run.
 *
 * The PNG comes back at the browser's DEVICE PIXEL RATIO, normally 2x: a frame
 * of 928 renders 1848 wide. Every width, gap and coordinate you read off a
 * render is in RENDER pixels. Divide by (png width / frame width) before
 * comparing anything to a measurement taken off the subject, or use
 * `--scale 0.5` to pin the export to 1:1. A weight ladder read without this
 * comes back at double, which is three nibs of error.
 *
 * Three flags have traps in them, all paid for:
 *
 * --only / --hide match a mark's STAGE (when in the ladder it was made) or its
 *         TAG (which object it belongs to) -- pen.stroke takes both, and they
 *         are independent axes. `--only ink,frame` is the whole panel's ink;
 *         `--only bike,frame` is the bicycle at every stage; and
 *         `--only bike,blockin,frame` is the bicycle over the composition
 *         rough, which is the view a detail pass on one object needs.
 * --only  is --hide's complement: keep these stages, drop the rest. It is what
 *         a study is made of -- one object worked to full depth over a faded
 *         composition rough, without leaving the panel's coordinate space, so
 *         it is registered from its first mark. INCLUDE `frame` IN THE LIST,
 *         or the render bounds collapse to the shapes you kept and every crop
 *         taken against it means something different.
 * --padding 0  makes the frame clip as well as pin. Contours then run past it,
 *         as they should, and fall off the edge instead of dragging the border
 *         out and leaving a margin of bare paper the drawing never reaches.
 *         Use it with pen.frame() whenever working from a reference, so every
 *         render shares the subject's coordinate space and overlay is exact.
 * --palette  repoints any of the 13 stock colour names at a real hex value.
 *         `background` is repointable too, but it is the ground, not a
 *         fourteenth colour: a mark may not use it. Measure it off the subject
 *         -- see pen.write's docstring for what a wrong ground costs.
 */
import { createServer } from 'node:http'
import { readFile, writeFile } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { extname, join, dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright'

const HERE = dirname(fileURLToPath(import.meta.url))
const DIST = join(HERE, 'dist')

const TYPES = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2',
}

function serve() {
  const server = createServer(async (request, response) => {
    const path = request.url.split('?')[0]
    const file = join(DIST, path === '/' ? 'index.html' : path)
    try {
      const body = await readFile(file)
      response.writeHead(200, { 'content-type': TYPES[extname(file)] ?? 'application/octet-stream' })
      response.end(body)
    } catch {
      response.writeHead(404).end('not here')
    }
  })
  return new Promise((ok) => server.listen(0, () => ok({ server, port: server.address().port })))
}

function flag(name, fallback = null) {
  const at = process.argv.indexOf(`--${name}`)
  return at === -1 ? fallback : process.argv[at + 1]
}

// Repeatable flags. `--hide ink --hide touches` is the form anyone writes first,
// and taking only the first occurrence dropped the second in silence -- the
// render came back looking plausible and hiding one stage fewer than asked.
function flags(name) {
  const found = []
  process.argv.forEach((word, at) => {
    if (word === `--${name}` && process.argv[at + 1]) {
      found.push(...process.argv[at + 1].split(','))
    }
  })
  return found
}

async function main() {
  const docPath = process.argv[2]
  if (!docPath || docPath.startsWith('--')) {
    console.error(
      'usage: node cli.mjs <doc.json> [--ops ops.json] [--png out.png]\n' +
      '                    [--scale N] [--flip] [--squint PX] [--crop x,y,w,h]\n' +
      '                    [--palette colours.json] [--padding N]\n' +
      '                    [--hide stage]...  (repeatable, or one comma list)\n' +
      '                    [--only stage]...  keep ONLY these stages (a study)'
    )
    process.exit(2)
  }
  if (!existsSync(DIST)) {
    console.error('harness not built -- run: npm run build')
    process.exit(2)
  }

  const opsPath = flag('ops')
  const pngPath = flag('png')
  const scale = Number(flag('scale', '1'))
  const flip = process.argv.includes('--flip')
  const squint = Number(flag('squint', '0'))
  const crop = flag('crop') ? flag('crop').split(',').map(Number) : null
  const padding = Number(flag('padding', '32'))
  const hide = flags('hide')
  const only = flags('only')

  const { server, port } = await serve()
  const browser = await chromium.launch()
  const page = await browser.newPage({ viewport: { width: 1400, height: 1000 } })
  const trouble = []
  page.on('pageerror', (error) => trouble.push(String(error)))
  page.on('console', (message) => {
    if (message.type() === 'error') trouble.push(message.text())
  })

  try {
    await page.goto(`http://localhost:${port}/`)
    await page.waitForFunction('window.canvasReady === true', { timeout: 30000 })

    const palettePath = flag('palette')
    if (palettePath) {
      const palette = JSON.parse(await readFile(palettePath, 'utf8'))
      await page.evaluate((colours) => window.canvas.repaint(colours), palette)
    }

    if (existsSync(docPath)) {
      const doc = JSON.parse(await readFile(docPath, 'utf8'))
      await page.evaluate((snapshot) => window.canvas.load(snapshot), doc)
    }

    if (opsPath) {
      const ops = JSON.parse(await readFile(opsPath, 'utf8'))
      const made = await page.evaluate((batch) => window.canvas.apply(batch), ops)
      console.log(`applied ${ops.length} ops, ${made.length} new strokes`)
    }

    const census = await page.evaluate(() => window.canvas.census())
    console.log('on the page:', JSON.stringify(census))

    await writeFile(docPath, JSON.stringify(await page.evaluate(() => window.canvas.save())))

    if (pngPath) {
      const encoded = await page.evaluate(
        (options) => window.canvas.shot(options),
        { scale, flip, squint, crop, padding, hide, only }
      )
      if (encoded === null) {
        console.log('nothing on the page to render')
      } else {
        await writeFile(pngPath, Buffer.from(encoded, 'base64'))
        console.log(`rendered ${pngPath}`)
      }
    }
  } finally {
    await browser.close()
    server.close()
  }

  if (trouble.length) {
    console.error('page trouble:\n  ' + trouble.slice(0, 5).join('\n  '))
    process.exit(1)
  }
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
