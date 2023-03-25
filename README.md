# lang.org.ua
http://lang.org.ua website

Here is some examples of typography with `inline code`

```python
with some(good, examples):
  of(indentation)
```

## A note to my future self:
 * export corpus via admin
 * split it in chunks like this: `cat ubertext.news.filter_rus_gcld+short.text_only.txt | pv | split -l5000000 --additional-suffix .txt -d - split/news_`
 * apply text normalization: `JAVA_TOOL_OPTIONS=-Xmx128G groovy CleanText.groovy --dir split/ -w 2 -p` (be careful with RAM usage)
 * glue all the normalized parts back together and apply sed to replace \n{3,} to \n\n\n\n, like this sed -z 's/\n\{3,\}/\n\n\n\n/g. Or more precisely: `cat fiction_00.txt  fiction_01.txt  fiction_02.txt  fiction_03.txt | pv -cN "Input"| sed -z 's/\n\{3,\}/\n\n\n\n/g' | pv -cN "Output" > ubertext.fiction.filter_rus_gcld+short.text_only.txt` or maybe even:
 `$ rm ubertext.court.filter_rus_gcld+short.text_only.txt; for file in court_*.txt; do cat $file | sed -z 's/\n\{3,\}/\n\n\n\n/g' | pv -cN "$file"  >> ubertext.court.filter_rus_gcld+short.text_only.txt; done`

 * apply sentence tokenizer: `cat /data/ubertext/for_stefan/fiction/ready-clean/ubertext.fiction.filter_rus_gcld+short.text_only.txt | pv -cN "Input" | groovy TokenizeText.groovy -s -i - -o - | pv -cN "Output" > /data/ubertext/for_stefan/fiction/ready-sentenced/ubertext.fiction.filter_rus_gcld+short.text_only.txt`