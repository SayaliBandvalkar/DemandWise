import base64

with open('frontend/public/logo-icon.png', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode('utf-8')

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <image href="data:image/png;base64,{b64}" width="256" height="256"/>
</svg>
'''

with open('frontend/public/favicon.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

print("favicon.svg successfully generated!")
