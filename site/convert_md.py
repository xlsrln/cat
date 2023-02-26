import markdown

def convert_md(filename):
    with open(filename, 'r') as f:
        text = f.read()

        outputname = filename.replace(".md", ".html")
        text = text.replace(".md", ".html").replace("s1/", "")

        html = markdown.markdown(text, extensions=['tables'])

        style = f"""
        <!doctype html><html lang="en"><head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="github-markdown.css">
        <link rel="icon" type="image/png" sizes="32x32" href="favicons/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="96x96" href="favicons/favicon-96x96.png">
        <link rel="icon" type="image/png" sizes="16x16" href="favicons/favicon-16x16.png">
        <title>catface {filename.replace('.md', ' ')}</title>"""

        style = style + """
        <style>
        .markdown-body {
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 45px;
        }

        @media (max-width: 767px) {
                .markdown-body {
                        padding: 15px;
                }
        }
        </style>
        <article class="markdown-body">"""

        html = style + html
        html = html.replace("<table", '<table align="center"')

    with open(outputname, 'w') as f:
        f.write(html)

    return outputname


for x in ['s1_index.md', 's1_teams.md', 's1_results.md', 's1_stages.md', 's1_finale.md',
            'index.md', 'setup.md', 'stages.md', 'rules.md', 'teams.md',
            'results.md']:
    f = convert_md(x)
    print("saving ", f)
