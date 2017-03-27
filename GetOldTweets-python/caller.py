import demo
import shlex
cmd = '--querysearch "#demonetisation OR #demonetization :)" --since 2016-11-08 --until 2016-11-09 --toptweets --maxtweets 3000 --outputfile demofile_pos.csv'
demo.main(shlex.split(cmd))