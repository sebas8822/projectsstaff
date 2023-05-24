import 'package:flutter/material.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: const Text('Web Auth 2 example'),
        ),
        body: AuthScreen(),
      ),
    );
  }
}

class AuthScreen extends StatefulWidget {
  @override
  _AuthScreenState createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  String _status = '';
  String _pictureUrl = '';
  String _firstName = '';
  String _lastName = '';
  String _emailAddress = '';

  Future<void> authenticate() async {
    setState(() {
      _status = 'Authenticating...';
    });

    final url = 'https://www.linkedin.com/oauth/v2/authorization?'
        'response_type=code&'
        'client_id=86huxyar2l3rkb&'
        'redirect_uri=http://localhost:52983/auth.html&'
        'scope=r_liteprofile%20r_emailaddress';

    final result = await FlutterWebAuth2.authenticate(
      url: url,
      callbackUrlScheme: 'http',
    );

    final code = handleAuthResultCode(result);
    if (code != null) {
      await requestAccessToken(code);
    }

    setState(() {
      _status = 'Result: $result';
    });
  }

  String? handleAuthResultCode(String result) {
    final currentUri = Uri.parse(result);

    if (currentUri.queryParameters.containsKey('code')) {
      final code = currentUri.queryParameters['code'];
      return code;
    }

    return null;
  }

  Future<void> requestAccessToken(String code) async {
    final url = Uri.parse('https://www.linkedin.com/oauth/v2/accessToken');
    final headers = {'Content-Type': 'application/x-www-form-urlencoded'};
    final body = {
      'grant_type': 'authorization_code',
      'client_id': '86huxyar2l3rkb',
      'client_secret': 'Cx9cLaatuW5huwQf',
      'code': code,
      'redirect_uri': 'http://localhost:52983/auth.html',
    };

    try {
      final response = await http.post(url, headers: headers, body: body);

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        final accessToken = jsonResponse['access_token'];
        await getProfile(accessToken);
      } else {
        print('Request failed with status: ${response.statusCode}');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  Future<void> getProfile(String accessToken) async {
    final url = Uri.parse('https://api.linkedin.com/v2/me');
    final headers = {'Authorization': 'Bearer $accessToken'};

    try {
      final response = await http.get(url, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        getPicture(accessToken);
        setState(() {
          _firstName = jsonResponse['firstName']['localized']['es_ES'];
          _lastName = jsonResponse['lastName']['localized']['es_ES'];
        });

        await requestEmailAddress(accessToken);
      } else {
        print('Request failed with status: ${response.statusCode}');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  Future<void> getPicture(String accessToken) async {
    final url = Uri.parse(
        'https://api.linkedin.com/v2/me?projection=(profilePicture(displayImage~:playableStreams))');
    final headers = {'Authorization': 'Bearer $accessToken'};

    try {
      final response = await http.get(url, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        final profilePic = jsonResponse['profilePicture']['displayImage~']
            ['elements'][0]['identifiers'][0]['identifier'];

        setState(() {
          _pictureUrl = profilePic;
        });

        print('Profile Picture: $_pictureUrl');
      } else {
        print('Request failed with status: ${response.statusCode}');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  Future<void> requestEmailAddress(String accessToken) async {
    final url = Uri.parse(
        'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))');
    final headers = {'Authorization': 'Bearer $accessToken'};

    try {
      final response = await http.get(url, headers: headers);

      if (response.statusCode == 200) {
        final jsonResponse = jsonDecode(response.body);
        final email = jsonResponse['elements'][0]['handle~']['emailAddress'];
        setState(() {
          _emailAddress = email;
        });
      } else {
        print('Request failed with status: ${response.statusCode}');
      }
    } catch (e) {
      print('Error: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          if (_pictureUrl.isNotEmpty) Image.network(_pictureUrl),
          Text('First Name: $_firstName'),
          Text('Last Name: $_lastName'),
          Text('Email Address: $_emailAddress'),
          const SizedBox(height: 80),
          ElevatedButton(
            onPressed: authenticate,
            child: const Text('Authenticate with LinkedIn'),
          ),
        ],
      ),
    );
  }
}
