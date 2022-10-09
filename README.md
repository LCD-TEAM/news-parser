# news-parser
## HOW TO USE:
first argument is for the portal you want to use, variants:
- `--rbc` - to use rbc.ru
- `--lenta` - to use lenta.ru
- `--buhru` - to use buh.ru
- `--bankiru` - to use banki.ru
- `--gartner` - to use gartner.com

for **lenta**, **buhru** and **bankiru** you also need to specify the start+end dates with `-from *YYYY-mm-dd*` and `-to *YYYY-mm-dd*`
for gartner you also need to specify number of articles to scrap with `-articles *number of articles*`
for all portals you shoud specify the output file name with `-o *filename*` otherwise it will be named **\*used portal name\*.csv**
you can find all generated .csv files in **data/**
## EXAMPLE:
`python main.py --buhru -start 2022-10-01 -end 2022-10-07 -o buhru123.csv`