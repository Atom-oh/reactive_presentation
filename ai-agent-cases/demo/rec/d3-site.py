"""D3: assembly.whchoi.net (22대 국회 온톨로지 데모 앱) 화면 녹화. Playwright recordVideo, 1920x1080.

녹화 화면에는 커서와 단계 자막(아래쪽 노란 띠)만 덧붙입니다. 사이트 화면과 응답은 녹화 시점 그대로입니다.
Usage: python d3-site.py <out_dir>
"""
import asyncio
import sys

from playwright.async_api import async_playwright

BASE = "https://assembly.whchoi.net"
OVERLAY = """
(() => {
  if (document.getElementById('__rec_cursor')) return;
  const c = document.createElement('div'); c.id = '__rec_cursor';
  Object.assign(c.style, {position:'fixed', width:'22px', height:'22px', borderRadius:'50%', border:'3px solid #ffd400',
    background:'rgba(255,212,0,.25)', zIndex:2147483647, pointerEvents:'none', transform:'translate(-50%,-50%)', left:'-50px', top:'-50px'});
  const cap = document.createElement('div'); cap.id = '__rec_caption';
  Object.assign(cap.style, {position:'fixed', left:'50%', bottom:'28px', transform:'translateX(-50%)', zIndex:2147483646,
    background:'#ffd400', color:'#111', font:'600 26px "Noto Sans CJK KR", sans-serif', padding:'10px 26px', borderRadius:'10px',
    boxShadow:'0 6px 24px rgba(0,0,0,.45)', pointerEvents:'none', maxWidth:'1500px', textAlign:'center'});
  document.addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
  document.addEventListener('mousedown', () => { c.style.background = 'rgba(255,212,0,.8)'; }, true);
  document.addEventListener('mouseup', () => { c.style.background = 'rgba(255,212,0,.25)'; }, true);
  const add = () => { document.body.appendChild(c); document.body.appendChild(cap); cap.textContent = sessionStorage.getItem('__cap') || ''; cap.style.display = cap.textContent ? 'block' : 'none'; };
  if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);
})();
"""


async def caption(pg, text):
    await pg.evaluate("t => { sessionStorage.setItem('__cap', t); const c = document.getElementById('__rec_caption');"
                      " if (c) { c.textContent = t; c.style.display = t ? 'block' : 'none'; } }", text)


async def move_click(pg, loc, dbl=False, pause=700):
    await loc.scroll_into_view_if_needed()
    box = await loc.bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    await pg.mouse.move(x, y, steps=30)
    await pg.wait_for_timeout(pause)
    if dbl:
        await pg.mouse.dblclick(x, y)
    else:
        await pg.mouse.click(x, y)


async def smooth_scroll(pg, dy, steps=40):
    for _ in range(steps):
        await pg.mouse.wheel(0, dy / steps)
        await pg.wait_for_timeout(35)


async def main(out):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=1,
                                  record_video_dir=out, record_video_size={"width": 1920, "height": 1080}, locale="ko-KR")
        await ctx.add_init_script(OVERLAY)
        pg = await ctx.new_page()
        await pg.mouse.move(960, 540)

        # 1. 온톨로지 스키마: 클래스 목록
        await pg.goto(f"{BASE}/objects", wait_until="networkidle")
        await caption(pg, "① Object Explorer: 온톨로지의 클래스(개념) 31개. 인물, 입법, 주제, 미디어, 독자, 광고")
        await pg.wait_for_timeout(3500)
        await smooth_scroll(pg, 700)
        await pg.wait_for_timeout(2000)
        await smooth_scroll(pg, -700)
        await move_click(pg, pg.get_by_text("Person", exact=True).first)
        await pg.wait_for_load_state("networkidle")
        await caption(pg, "② 클래스 Person의 인스턴스(개체) 306개. 실제 데이터 출처 표시")
        await pg.wait_for_timeout(3500)

        # 2. 한 개체의 관계 그래프
        await pg.goto(f"{BASE}/mindmap", wait_until="networkidle")
        await caption(pg, "③ 관계 그래프 탐색: 시작 개체 유형과 의원을 고른다")
        await pg.wait_for_timeout(2500)
        await move_click(pg, pg.get_by_text("김태년", exact=True).first)
        await pg.wait_for_load_state("networkidle")
        await pg.wait_for_timeout(1500)
        graph = pg.get_by_text("온톨로지 관계 그래프 (1-hop)", exact=False).first
        await graph.scroll_into_view_if_needed()
        await smooth_scroll(pg, 380)
        await caption(pg, "④ 1-hop: 의원 노드에서 정당, 위원회, 발의 의안, 표결, 주제로 바로 이어진 관계(엣지)")
        await pg.wait_for_timeout(5500)
        await move_click(pg, pg.get_by_role("button", name="2-hop"))
        await caption(pg, "⑤ 2-hop: 의안을 거쳐 공동발의 의원과 그 의원의 위원회, 의안까지 (Neptune multi-hop 조회)")
        await pg.wait_for_timeout(8000)
        await move_click(pg, pg.get_by_role("button", name="1-hop"))
        await pg.wait_for_timeout(3500)
        # 3. 같은 온톨로지 위의 에이전트
        await pg.goto(f"{BASE}/chat", wait_until="networkidle")
        await caption(pg, "⑥ 데스크 챗봇: 같은 온톨로지를 도구로 조회하는 에이전트")
        await pg.wait_for_timeout(3000)
        await move_click(pg, pg.get_by_text("AI 관련 의안 발의 상위 5명", exact=False).first)
        await caption(pg, "⑦ 에이전트가 planner, graph, analyst, editor 순서로 일하고, 호출한 도구가 오른쪽 로그에 남는다")
        for _ in range(60):
            await pg.wait_for_timeout(1000)
            if await pg.get_by_text("editor", exact=False).count() >= 2:
                break
        await pg.wait_for_timeout(6000)
        await pg.wait_for_timeout(2500)
        await caption(pg, "⑧ 답에는 근거 수치와 출처(국회 OpenAPI, 합성 데이터)가 함께 표시된다")
        await smooth_scroll(pg, 450, 60)
        await pg.wait_for_timeout(5000)
        await smooth_scroll(pg, 600, 60)
        await pg.wait_for_timeout(4000)
        await caption(pg, "")
        await pg.wait_for_timeout(1000)
        path = await pg.video.path()
        await ctx.close()
        await b.close()
        print(path)


asyncio.run(main(sys.argv[1]))
