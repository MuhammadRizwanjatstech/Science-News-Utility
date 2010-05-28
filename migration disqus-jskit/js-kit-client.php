<?php

class JSKit_Client {
	var $jsKitUser = NULL;
	var $http_client = NULL;
	var $url_prefix = 'http://js-kit.com';

	function JSKit_Client($http_client, $jsKitUser = null) {

		$this->http_client = $http_client;
		$this->setjsKitUser($jsKitUser);
	}

	function getjsKitUser() {

		return $this->jsKitUser;
	}

	function setjsKitUser($jsKitUser) {

		if (!is_null($jsKitUser) && is_string($jsKitUser) && strlen($jsKitUser) > 0) {
			$this->jsKitUser = $jsKitUser;
		}
	}

	function http_request($method, $url, $params = NULL, $aux_params = NULL, $data = NULL, $headers = NULL) {

		if (!in_array($method, array('get', 'post'))) {
			return array('400', 'Bad request method');
		}

		if (empty($url)) {
			return array('400', 'Bad request URL');
		}

		if (isset($aux_params) && is_array($aux_params)) {
			foreach($aux_params as $k => $v) {
				$params[$k] = $v;
			}
		}

		$request_cookies = array();
		if (!empty($this->jsKitUser)) {
			$request_cookies['jsKitUser'] = $this->jsKitUser;;
		}

		$result = $this->http_client->request($method, $url, $params, $data, $request_cookies, $headers);

		#var_dump($result);

		if (!empty($result['error'])) {
			return array(500, $result['error']);
		}

		if (!empty($result['cookies']) && is_array($result['cookies']) && isset($result['cookies']['jsKitUser'])) {
			$this->setjsKitUser($result['cookies']['jsKitUser']);
		}

		return array($result['http_code'], $result['body']);
	}

	function get_comments($domain, $path, $aux_params = NULL) {

		if (empty($domain) || empty($path)) {
			return array(500, 'Please pass domain and path attributes');
		}

		$url = $this->url_prefix."/comments-data.js";
		$params = array(
			# Sort Field. srt = [date|name|karma]
			'srt' => 'date',
			# Sort Order. ord = [asc|desc]
			'ord' => 'asc',
			# Unique location of a comment roll = Domain plus Path value.
			# Example: http://example.com/path
			'ref' => 'http://'.$domain.$path
		);

		$headers = array(
			'Referer' => $params['ref'],
		);

		return $this->http_request('get', $url, $params, $aux_params, NULL, $headers);
	}

	function add_comment($domain, $path, $permalink, $name, $text, $email = NULL, $in_reply_to_comment_id = NULL, $aux_params = NULL) {

		if (empty($domain) || empty($path) || empty($permalink) || empty($name) || empty($text)) {
			return array(500, 'Please pass domain, path, permalink, name and text attributes');
		}

		$url = $this->url_prefix."/comment.put";
		$params = array(
			'tid'         => 'jst-1',
			#'avatar'      => 'no',
			'js-CmtName'  => $name,
			'js-CmtText'  => $text,
			'js-CmtEmail' => $email,
			# URL of a page the comment was posted from.
			'permalink'   => $permalink,
			# Unique location of a comment roll = Domain plus Path value.
			# Example: http://example.com/path
			'ref' => 'http://'.$domain.$path
		);

		# If the comment is a reply to another comment.
		if (!is_null($in_reply_to_comment_id) && is_string($in_reply_to_comment_id) && strlen($in_reply_to_comment_id) > 0) {
			$params['js-CmtParentID'] = $in_reply_to_comment_id;
		}

		$headers = array(
			'Referer' => $permalink
		);

		return $this->http_request('get', $url, $params, $aux_params, NULL, $headers);
	}

	function delete_comment($domain, $path, $comment_id, $aux_params = NULL) {

		if (empty($domain) || empty($path) || empty($comment_id)) {
			return array(500, 'Please pass domain, path and comment_id attributes');
		}

		$url = $this->url_prefix."/comment.del";
		$params = array(
			'jx'  => 0,
			'id'  => $comment_id,
			# Unique location of a comment roll = Domain plus Path value.
			# Example: http://example.com/path
			'ref' => 'http://'.$domain.$path
		);

		$headers = array(
			'Referer' => $params['ref'],
		);

		return $this->http_request('get', $url, $params, $aux_params, NULL, $headers);
	}
}


class JSKit_HTTP_Client {
	var $timeout = NULL; 

	function JSKit_HTTP_Client($timeout = 10) {
		if (!extension_loaded("curl")) {
			die("JSKit_HTTP_Client requires presence of curl PHP extension");
		}

		if (is_numeric($timeout) && $timeout >= 0) {
			$this->timeout = intval($timeout);
		}
	}

	function request($method, $url, $params = NULL, $data = NULL, $cookies = NULL, $headers = NULL) {

		$ch = curl_init();
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
		curl_setopt($ch, CURLOPT_HEADER, true);
		curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);
		curl_setopt($ch, CURLOPT_USERAGENT, 'JSKit_HTTP_Client/1.0');

		# Set Request URL
		$query_string = '';
		if (!empty($params) && is_array($params)) {
			foreach ($params as $k => $v) {
				$query_string[] = urlencode($k) . '=' . urlencode($v);
			}
			$query_string = join("&", $query_string);
		}
		curl_setopt($ch, CURLOPT_URL, $url . ($query_string ? '?' . $query_string : ''));

		# Set Request POST data if Request Method is POST.
		if (strtolower($method) == 'post') {
			curl_setopt($ch, CURLOPT_POST, true);
			if (!empty($data) && is_array($data)) {
				$request_data = '';
				foreach($data as $k => $v) {
					$request_data[] = urlencode($k) . '=' . urlencode($v);
				}
				$request_data = join("&", $request_data);
				curl_setopt($ch, CURLOPT_POSTFIELDS, $request_data);
			}
		}

		# Set request cookies.
		if (!empty($cookies) && is_array($cookies)) {
			$request_cookies = array();
			foreach ($cookies as $k => $v) {
				$request_cookies[] = $k . '=' . $v;
			}
			$request_cookies = join(";", $request_cookies);
			curl_setopt($ch, CURLOPT_COOKIE, $request_cookies);
		}

		# Set Request headers
		if (!empty($headers) && is_array($headers)) {
			$request_headers = array();
			foreach ($headers as $k => $v) {
				$request_headers[] = $k . ': ' . $v;
			}
			curl_setopt($ch, CURLOPT_HTTPHEADER, $request_headers);
		}

		#echo "request url: " . $url . ($query_string ? '?' . $query_string : '') .  "\n";
		# Perform request
		$response = curl_exec($ch);

		# Parse response
		$result = array(
			'error' => '',
			'http_code' => '',
			'headers' => '',
			'cookies' => array(),
			'body' => ''
		);

		$error = curl_error($ch);
		if (!empty($error)) {
			$result['error'] = $error;

			return $result;
		}

		$result['http_code'] = curl_getinfo($ch, CURLINFO_HTTP_CODE);
		$header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
		if ($header_size > 0) {
			$result['headers'] = substr($response, 0, $header_size);
			$result['cookies'] = $this->parse_cookies($result['headers']);
		}
		$result['body'] = substr($response, $header_size);

		return $result;
	}

	# Parses a string with headers and returns an array with cookie values.
	function parse_cookies($headers) {
		if (!is_string($headers) || strlen($headers) == 0) {
			return array();
		}

		$header_lines = split("\n", $headers);
		$cookies = array();
		if (!empty($header_lines) && is_array($header_lines)) {
			foreach ($header_lines as $header_line) {
				list($header_name, $header_value) = split(': ', $header_line, 2);
				if ($header_name == 'Set-Cookie') {
					$cookie_values = split(';', $header_value);
					if (!empty($cookie_values) && is_array($cookie_values)) {
						list($cookie_name, $cookie_value) = split('=', $cookie_values[0], 2);
						$cookies[trim($cookie_name)] = trim($cookie_value);
					}
				}
			}
		}

		return $cookies;
	}
}

$jsk_http_client = new JSKit_HTTP_Client();
$jsk_client = new JSKit_Client($jsk_http_client);

echo "\n\n";
echo "jsKitUser: " . var_export($jsk_client->getjsKitUser(), true) . "\n";
echo "Getting list of comments\n";
list($error_code, $response) = $jsk_client->get_comments('example.com', '/test7');
var_dump($error_code);
var_dump($response);
echo "jsKitUser: " . var_export($jsk_client->getjsKitUser(), true) . "\n";

echo "Adding new comment\n";
list($error_code, $response) = $jsk_client->add_comment('example.com', '/test7', 'http://example.com/test.html', 'Tester', 'Test Comment rnd: ' . rand(1,100), 'tester@example.com');
var_dump($error_code);
var_dump($response);
echo "jsKitUser: " . var_export($jsk_client->getjsKitUser(), true) . "\n";
$comment_id = '';
if (preg_match("/'(jsid-\d+-\d+?)'/", $response, $m)) {
	$comment_id = $m[1];
	echo "Created comment: $comment_id\n";
}

if ($comment_id) {
	echo "Adding a reply\n";
	list($error_code, $response) = $jsk_client->add_comment('example.com', '/test7', 'http://example.com/test.html', 'Tester', 'Test Comment rnd: ' . rand(1,100), 'tester@example.com', $comment_id);
	var_dump($error_code);
	var_dump($response);
	echo "jsKitUser: " . var_export($jsk_client->getjsKitUser(), true) . "\n";
	$reply_comment_id = '';
	if (preg_match("/'(jsid-\d+-\d+?)'/", $response, $m)) {
		$reply_comment_id = $m[1];
		echo "Reply: $reply_comment_id\n";
	}

	if ($reply_comment_id) {
		list($error_code, $response) = $jsk_client->delete_comment('example.com', '/test7', $reply_comment_id);
		var_dump($error_code);
		var_dump($response);
		echo "jsKitUser: " . var_export($jsk_client->getjsKitUser(), true) . "\n";
	}
}

?>
