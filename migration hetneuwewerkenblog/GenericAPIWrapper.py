#! /usr/bin/env python
__author__ = 'jue@jueseph.com'
__version__ = '0.1-devel'

import os
import sys
import pickle
import tempfile
import simplejson
import httplib
import urllib
import urllib2
import cookielib
import urlparse
try:
  from hashlib import md5
except ImportError:
  from md5 import md5


class APIError(Exception):
    pass

class GenericAPIWrapper:
    DEFAULT_CACHE_TIMEOUT = 60 # cache for 1 minute

    _API_REALM = 'Twitter API'

    def __init__(self,
                 username=None,
                 password=None,
                 input_encoding=None,
                 request_headers=None,
                 debug_level=0):
        '''Instantiate a new GenericAPIWrapper object.

        Args:
          username: The username of the API account.  [optional]
          password: The password for the API account. [optional]
          input_encoding: The encoding used to encode input strings. [optional]
          request_header: A dictionary of additional HTTP request headers. [optional]
        '''
        self._cache = _FileCache()
        self._urllib = urllib2
        self._cache_timeout = GenericAPIWrapper.DEFAULT_CACHE_TIMEOUT
        self._InitializeRequestHeaders(request_headers)
        self._InitializeUserAgent()
        self._InitializeDefaultParameters()
        self._input_encoding = input_encoding
        self._debug_level = debug_level
        self.SetCredentials(username, password)

    def SetDebug(debug_level):
        self._debug_level = debug_level

    def SetCredentials(self, username, password):
        '''Set the username and password for this instance

        Args:
          username: The username.
          password: The password.
        '''
        self._username = username
        self._password = password

    def ClearCredentials(self):
        '''Clear the username and password for this instance
        '''
        self._username = None
        self._password = None

    def SetCache(self, cache):
        '''Override the default cache.  Set to None to prevent caching.

        Args:
            cache: an instance that supports the same API as the  twitter._FileCache
        '''
        self._cache = cache

    def SetUrllib(self, urllib):
        '''Override the default urllib implementation.

        Args:
            urllib: an instance that supports the same API as the urllib2 module
        '''
        self._urllib = urllib

    def SetCacheTimeout(self, cache_timeout):
        '''Override the default cache timeout.

        Args:
            cache_timeout: time, in seconds, that responses should be reused.
        '''
        self._cache_timeout = cache_timeout

    def SetUserAgent(self, user_agent):
        '''Override the default user agent

        Args:
            user_agent: a string that should be send to the server as the User-agent
        '''
        self._request_headers['User-Agent'] = user_agent

    def _BuildUrl(self, url, path_elements=None, extra_params=None):
        # Break url into consituent parts
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)

        # Add any additional path elements to the path
        if path_elements:
            # Filter out the path elements that have a value of None
            p = [i for i in path_elements if i]
            if not path.endswith('/'):
                path += '/'
                path += '/'.join(p)

        # Add any additional query parameters to the query string
        if extra_params and len(extra_params) > 0:
            extra_query = self._EncodeParameters(extra_params)
            # Add it to the existing query
            if query:
                query += '&' + extra_query
            else:
                query = extra_query

        # Return the rebuilt URL
        return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))

    def _InitializeRequestHeaders(self, request_headers):
        if request_headers:
            self._request_headers = request_headers
        else:
            self._request_headers = {}

    def _InitializeUserAgent(self):
        user_agent = 'Python-urllib/%s (python-twitter/%s)' % \
                (self._urllib.__version__, __version__)
        self.SetUserAgent(user_agent)

    def _InitializeDefaultParameters(self):
        self._default_params = {}

    def _AddAuthorizationHeader(self, username, password):
        if username and password:
            basic_auth = base64.encodestring('%s:%s' % (username, password))[:-1]
            self._request_headers['Authorization'] = 'Basic %s' % basic_auth

    def _RemoveAuthorizationHeader(self):
        if self._request_headers and 'Authorization' in self._request_headers:
            del self._request_headers['Authorization']

    def _GetOpener(self, url, username=None, password=None, auth_cookie=None):
        if username and password:
            self._AddAuthorizationHeader(username, password)
            handler = self._urllib.HTTPBasicAuthHandler()
            (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
            handler.add_password(Api._API_REALM, netloc, username, password)
            opener = self._urllib.build_opener(handler)
        elif auth_cookie:
            cj = cookielib.LWPCookieJar()
            cj.set_cookie(auth_cookie)
            opener = self._urllib.build_opener(urllib2.HTTPCookieProcessor(cj))
        else:
            opener = self._urllib.build_opener()
            opener.addheaders = self._request_headers.items()
        return opener

    def _Encode(self, s):
        if self._input_encoding:
            if self._input_encoding == 'utf-8':
                return s
            else:
                return unicode(s, self._input_encoding).encode('utf-8')
        else:
            return unicode(s).encode('utf-8')

    def _EncodeParameters(self, parameters):
        '''Return a string in key=value&key=value form

        Values of None are not included in the output string.

        Args:
            parameters:
                A dict of (key, value) tuples, where value is encoded as
                specified by self._encoding
        Returns:
            A URL-encoded string in "key=value&key=value" form
        '''
        if parameters is None:
            return None
        else:
            return urllib.urlencode(dict([(k, self._Encode(v)) for k, v in parameters.items() if v is not None]))

    def _EncodePostData(self, post_data):
        '''Return a string in key=value&key=value form

        Values are assumed to be encoded in the format specified by self._encoding,
        and are subsequently URL encoded.

        Args:
        post_data:
            A dict of (key, value) tuples, where value is encoded as
            specified by self._encoding
        Returns:
            A URL-encoded string in "key=value&key=value" form
        '''
        if post_data is None:
            return None
        else:
            return urllib.urlencode(dict([(k, self._Encode(v)) for k, v in post_data.items()]))

    def FetchUrl(self,
                 url,
                 post_data=None,
                 parameters=None,
                 auth_cookie=None,
                 dry_run=False,
                 no_cache=True,
                 convert_data=True,
                 verbose=False):
        '''Fetch a URL, optionally caching for a specified time.

        Args:
            url: The URL to retrieve
            post_data: 
                A dict of (str, unicode) key/value pairs.  If set, POST will be used.
            parameters:
                A dict whose key/value pairs should encoded and added 
                to the query string. [OPTIONAL]
            no_cache: If true, overrides the cache on the current request
            dry_run: If true, does not send any HTTP request. Use with SetDebug
            to display what would have been sent.
            convert_data: if 'True', converts data to Python dictionary.
            Default is True.

        Returns:
            A string containing the body of the response.
        '''
        # Build the extra parameters dict
        extra_params = {}
        if self._default_params:
            extra_params.update(self._default_params)
        if parameters:
            extra_params.update(parameters)

        # Add key/value parameters to the query string of the url
        url = self._BuildUrl(url, extra_params=extra_params)
        if self._debug_level > 0 or verbose:
            print 'Request sent:',url

        # Just testing, don't need to return data
        if dry_run:
            return None,None
        # Send HTTP request if not testing 
        else:
            # Get a url opener that can handle basic auth
            opener = self._GetOpener(url, username=self._username,
                                     password=self._password,
                                     auth_cookie=auth_cookie)

            encoded_post_data = self._EncodePostData(post_data)

            # Open and return the URL immediately if we're not going to cache
            if encoded_post_data or no_cache or not self._cache or not self._cache_timeout:
                response = opener.open(url, encoded_post_data)
                url_data = response.read()
                url_header = response.info()
                opener.close()
            else:
                # Unique keys are a combination of the url and the username
                if self._username:
                    key = self._username + ':' + url
                else:
                    key = url

                # See if it has been cached before
                last_cached = self._cache.GetCachedTime(key)

                # If the cached version is outdated then fetch another and store it
                if not last_cached or time.time() >= last_cached + self._cache_timeout:
                    response = opener.open(url, encoded_post_data)
                    url_data = response.read()
                    url_header = response.info()
                    opener.close()
                    self._cache.Set(key, (url_data, url_header))
                else:
                    url_data,url_header = self._cache.Get(key)

            # Return data as Python dict
            if convert_data:
                url_data = simplejson.loads(url_data)

            # Always return the latest version
            return url_data, url_header

class _FileCacheError(Exception):
    '''Base exception class for FileCache related errors'''

class _FileCache(object):

    DEPTH = 3

    def __init__(self,root_directory=None):
        self._InitializeRootDirectory(root_directory)

    def Get(self,key):
        path = self._GetPath(key)
        if os.path.exists(path):
            #return open(path).read()
            return simplejson.load(open(path,'r'))
        else:
            return None

    def Set(self,key,data):
        path = self._GetPath(key)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            if not os.path.isdir(directory):
                raise _FileCacheError('%s exists but is not a directory' % directory)
        temp_fd, temp_path = tempfile.mkstemp()
        temp_fp = os.fdopen(temp_fd, 'w')
        #temp_fp.write(data)
        simplejson.dump(data, temp_fp)
        temp_fp.close()
        if not path.startswith(self._root_directory):
            raise _FileCacheError('%s does not appear to live under %s' %
                                  (path, self._root_directory))
        if os.path.exists(path):
            os.remove(path)
            os.rename(temp_path, path)

    def Remove(self,key):
        path = self._GetPath(key)
        if not path.startswith(self._root_directory):
            raise _FileCacheError('%s does not appear to live under %s' %
                                  (path, self._root_directory ))
        if os.path.exists(path):
            os.remove(path)

    def GetCachedTime(self,key):
        path = self._GetPath(key)
        if os.path.exists(path):
            return os.path.getmtime(path)
        else:
            return None

    def _GetUsername(self):
        '''Attempt to find the username in a cross-platform fashion.'''
        try:
            return os.getenv('USER') or \
                    os.getenv('LOGNAME') or \
                    os.getenv('USERNAME') or \
                    os.getlogin() or \
                    'nobody'
        except (IOError, OSError), e:
            return 'nobody'

    def _GetTmpCachePath(self):
        username = self._GetUsername()
        cache_directory = 'python.cache_' + username
        return os.path.join(tempfile.gettempdir(), cache_directory)

    def _InitializeRootDirectory(self, root_directory):
        if not root_directory:
            root_directory = self._GetTmpCachePath()
            root_directory = os.path.abspath(root_directory)
            if not os.path.exists(root_directory):
                os.mkdir(root_directory)
                if not os.path.isdir(root_directory):
                    raise _FileCacheError('%s exists but is not a directory' %
                                          root_directory)
        self._root_directory = root_directory

    def _GetPath(self,key):
        try:
            hashed_key = md5(key).hexdigest()
        except TypeError:
            hashed_key = md5.new(key).hexdigest()

        return os.path.join(self._root_directory,
                        self._GetPrefix(hashed_key),
                        hashed_key)

    def _GetPrefix(self,hashed_key):
        return os.path.sep.join(hashed_key[0:_FileCache.DEPTH])

def testsuite():
    # A simple Twitter search, to test the API wrapper
    url = 'http://search.twitter.com/search.json'
    api = GenericAPIWrapper()
    data = api.FetchUrl(url, {'q':'climate change'})
    print 'Data fetched from',url+':'
    print data
    return 0

# Run this module to test
if __name__ == '__main__':
    status = testsuite()
    sys.exit(status)

