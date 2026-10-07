from glob import glob

dates = {}

with open("dates.txt") as f:
    for line in f:
        line = line.strip()
        name, date = line.split(": ")
        dates[name] = date

for name in glob("./**/*.md", recursive=True):
    '''
    # no files have a mising date
    if not name in dates:
        print(f'missing: {name}')
    '''

    with open(name) as f:
        lines = f.read()

    # remove ^./ and .md$ and get basename
    treated = name
    treated = treated[2:]
    treated = treated[:-3]

    base = treated.split('/')[1] if '/' in treated else treated
    title = ' '.join(b.capitalize() for b in base.split('-'))
   
    with open(name, "w") as f:
        fp = lambda content: print(content, file=f)
        fp("---")
        fp(f"title: {title}")
        fp(f"date: {dates[name]}")
        fp(f"description: TODO")
        fp("---")
        fp('')
        # until newline
        fp(lines[:-1])
