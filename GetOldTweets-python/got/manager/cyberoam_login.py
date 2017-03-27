import mechanize
import cookielib
from bs4 import BeautifulSoup
import ssl

def login():
	# Browser
	br = mechanize.Browser()
	

	# Cookie Jar
	cj = cookielib.LWPCookieJar()
	br.set_cookiejar(cj)

	# Browser options
	br.set_handle_equiv(True)
	br.set_handle_redirect(True)
	br.set_handle_referer(True)
	br.set_handle_robots(False)


	# Follows refresh 0 but not hangs on refresh > 0
	br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

	# User-Agent (this is cheating, ok?)
	br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36')]

	try:
		_create_unverified_https_context = ssl._create_unverified_context
	except AttributeError:
	     # Legacy Python that doesn't verify HTTPS certificates by default
		pass
	else:
		# Handle target environment that doesn't support HTTPS verification
		ssl._create_default_https_context = _create_unverified_https_context



	br.open('https://10.100.56.55:8090/httpclient.html')
	assert br.viewing_html()
	br.select_form(nr=0)

	br.form['username'] = '201301432'
	br.form['password'] = 'dharmil5533'

	br.submit()
	print 'Successfully logged in'

	br.close()

if __name__ == "__main__":
	login()