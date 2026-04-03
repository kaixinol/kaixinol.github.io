import niquests

session = niquests.Session()


data = session.get(
    'https://raw.githubusercontent.com/kaixinol/tools/refs/heads/main/tools.json'
).json()
sitemap =[]
for tool in data.keys():

    if 'url' in data[tool]:
        sitemap.append(
            f'<url><loc>/{data[tool]["url"].removeprefix("https://kaixinol.github.io/")}</loc></url>'
        )
    else:
        sitemap.append(f'<url><loc>/tools/{tool}</loc></url>')
print('\n'.join(sitemap))