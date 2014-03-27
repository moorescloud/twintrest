Twintrest - Simple Twitter sentiment analysis for Holiday by MooresCloud
========================================================================

Twintrest uses Twitter's search-and-match API calls to subscribe to a 
hashtag. Every time that hashtag appears in the firehose feed, a chaser light
runs up the Holiday.

The first time you run Twintrest it will ask you to authenticate against the 
application - this may require some cutting-and-pasting from the command line
into a browser, and back into the command line.

Useage is as follows:
<pre>
python twintrest.py hashtag ip-address-of-holiday
</pre>
Twintrest uses the <a href="https://github.com/moorescloud/secretapi">SecretAPI for Holiday</a> so it's quite speedy in its animations.

Mark Pesce<br/>
March 2014