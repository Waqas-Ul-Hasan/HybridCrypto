import asyncio
import os
import re
from playwright.async_api import async_playwright
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

def parse_rgb(color_str):
    # e.g., "rgb(255, 255, 255)" or "rgba(255, 255, 255, 0.5)"
    match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', color_str)
    if match:
        return RGBColor(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return RGBColor(255, 255, 255)

async def generate_ppt_editable():
    html_path = "file:///C:/FA23-BCS-A/IS/IS-Terminal/slides.html"
    out_pptx = "slides_editable.pptx"
    
    print("Launching headless browser to extract editable slides...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using 1280x720 for perfect scaling mapping
        viewport_w = 1280
        viewport_h = 720
        page = await browser.new_page(viewport={'width': viewport_w, 'height': viewport_h})
        await page.goto(html_path)
        
        # Hide the bottom navigation buttons and dots
        await page.evaluate("""
            document.querySelector('.nav').style.display = 'none';
            document.querySelector('.slide-counter').style.display = 'none';
        """)
        
        total = await page.evaluate("total")
        
        prs = Presentation()
        # Set presentation size to match viewport ratio and mapping
        # 1280x720 is 16:9. Let's make the PPT 13.333 x 7.5 inches (standard 16:9 PPT size)
        prs.slide_width = Inches(13.333333333)
        prs.slide_height = Inches(7.5)
        
        # Scale factor from browser pixels to PPT Inches
        scale_x = prs.slide_width / viewport_w
        scale_y = prs.slide_height / viewport_h
        
        blank_slide_layout = prs.slide_layouts[6] # Blank layout
        
        for i in range(total):
            await page.evaluate(f"goTo({i})")
            await page.wait_for_timeout(600) # wait for animations
            
            # Extract text data AND hide the text for the background screenshot
            js_script = """
            () => {
                const elements = [];
                const selectors = 'h1, h2, h3, p, li, th, td, .tag, .s1-lock, .big-check, .flow-box, .sec-label > span, .code-block';
                
                document.querySelectorAll(selectors).forEach(el => {
                    const slide = el.closest('.slide');
                    if (!slide || !slide.classList.contains('active')) return;
                    
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) return;
                    
                    const style = window.getComputedStyle(el);
                    
                    // We extract innerText which ignores hidden elements and formats nicely
                    let text = el.innerText.trim();
                    if (!text) return;
                    
                    elements.push({
                        text: text,
                        x: rect.x,
                        y: rect.y,
                        w: rect.width,
                        h: rect.height,
                        fontSize: style.fontSize, // "24px"
                        color: style.color,       // "rgb(...)"
                        textAlign: style.textAlign,
                        fontWeight: style.fontWeight
                    });
                    
                    // Hide the text but preserve layout geometry
                    el.style.setProperty('color', 'transparent', 'important');
                    el.style.setProperty('text-shadow', 'none', 'important');
                    // Hide any spans inside (like code blocks)
                    el.querySelectorAll('*').forEach(child => {
                        child.style.setProperty('color', 'transparent', 'important');
                        child.style.setProperty('text-shadow', 'none', 'important');
                    });
                });
                return elements;
            }
            """
            
            text_data = await page.evaluate(js_script)
            
            # Now take a screenshot of the "empty" background
            img_path = f"temp_slide_{i}.png"
            await page.screenshot(path=img_path)
            
            # Create the PPT slide
            slide = prs.slides.add_slide(blank_slide_layout)
            slide.shapes.add_picture(img_path, 0, 0, width=prs.slide_width, height=prs.slide_height)
            os.remove(img_path)
            
            # Restore the text colors in the browser so next slide transitions look okay
            await page.evaluate("""
                () => {
                    document.querySelectorAll('*').forEach(el => {
                        el.style.removeProperty('color');
                        el.style.removeProperty('text-shadow');
                    });
                }
            """)
            
            # Add editable text boxes
            for item in text_data:
                x = int(item['x'] * scale_x)
                y = int(item['y'] * scale_y)
                w = int(item['w'] * scale_x)
                # Expand height slightly to prevent text clipping in PPT
                h = int((item['h'] + 10) * scale_y)
                
                # Create text box
                txBox = slide.shapes.add_textbox(x, y, w, h)
                tf = txBox.text_frame
                tf.word_wrap = True
                
                # Remove default margins
                tf.margin_left = 0
                tf.margin_top = 0
                tf.margin_right = 0
                tf.margin_bottom = 0
                
                p = tf.paragraphs[0]
                p.text = item['text']
                
                # Font size
                font_size_px = float(item['fontSize'].replace('px', ''))
                # 1px = 0.75pt, but in PPT sometimes it needs slight tweaking
                p.font.size = Pt(font_size_px * 0.75)
                
                # Color
                p.font.color.rgb = parse_rgb(item['color'])
                
                # Bold
                if item['fontWeight'] in ['bold', '600', '700', '800', '900']:
                    p.font.bold = True
                    
                # Alignment
                align = item['textAlign']
                if align == 'center':
                    p.alignment = PP_ALIGN.CENTER
                elif align == 'right':
                    p.alignment = PP_ALIGN.RIGHT
                else:
                    p.alignment = PP_ALIGN.LEFT
                    
            print(f"  -> Processed editable slide {i+1}/{total}")
            
        await browser.close()
        
    prs.save(out_pptx)
    print(f"\n[OK] Editable hybrid presentation saved -> {out_pptx}")

if __name__ == "__main__":
    asyncio.run(generate_ppt_editable())
