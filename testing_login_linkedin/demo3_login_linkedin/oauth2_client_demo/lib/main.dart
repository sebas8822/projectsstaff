import 'package:flutter/material.dart';
import 'package:flutter_web_auth_2/flutter_web_auth_2.dart';
import 'package:http/http.dart' as http;
import 'dart:convert' show jsonDecode;


void main() {
  runApp(const MaterialApp(home: MyApp()));
}


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('LinkedIn Login Example')),
      body: Center(
        child: ElevatedButton(
          child: const Text('Authenticate with LinkedIn'),
          onPressed: () {
            _authenticateWithLinkedIn(context);
          },
        ),
      ),
    );
  }
}






/*
  
  void _authenticateWithLinkedIn(BuildContext context) async {
    OAuth2Client client = LinkedInOAuth2Client(
      redirectUri: redirectUrl,
      customUriScheme: 'http://localhost:8080',
    );

    print("esperando pasar................");
    AccessTokenResponse tknResp = await client.getTokenWithAuthCodeFlow(
      clientId: '86huxyar2l3rkb',
      clientSecret: 'Cx9cLaatuW5huwQf',
      scopes: ['r_liteprofile'],
    );

    print("esperando pasar..");
    if (tknResp != null) {
      // From now on, you can perform authenticated HTTP requests
      http.Client httpClient = http.Client();
      http.Response resp = await httpClient.get(
        Uri.parse('http://localhost/auth/linkedin/callback'),
        headers: {'Authorization': 'Bearer ${tknResp.accessToken}'},
      );

      print("hola si paso");
      print(resp);
    }
  }*/

  /*
  void _authenticateWithLinkedIn(BuildContext context) async {
    const authorizationUrl = 'https://www.linkedin.com/oauth/v2/authorization';
    const tokenUrl = 'https://www.linkedin.com/oauth/v2/accessToken';
    const scopes = ['r_liteprofile'];

    OAuth2Client liClient = LinkedInOAuth2Client(
      redirectUri: redirectUrl,
      customUriScheme: 'http://localhost:8080',
    );

    // Instantiate the helper passing the previously instantiated client
    OAuth2Helper oauth2Helper = OAuth2Helper(
      liClient,
      grantType: OAuth2Helper.authorizationCode,
      clientId: clientId,
      clientSecret: clientSecret,
      scopes: scopes,
    );

    AccessTokenResponse tknResp = await liClient.getTokenWithAuthCodeFlow(
        clientId: clientId, clientSecret: clientSecret, scopes: scopes);

    //From now on you can perform authenticated HTTP requests
    var httpClient = http.Client();
    http.Response resp = await httpClient.get(
        'https://api.github.com/user/repos',
        headers: {'Authorization': 'Bearer ' + tknResp.accessToken});

    /*
    print('Receiving Code.....');
    var result = await oauth2Helper.ge;
    print('Receiving Code after.....');
    final queryParams = html.window.location.search;
    print('queryParams: $queryParams');
    final code = Uri.splitQueryString(queryParams!)['code'];
    print('Received code121212: $code');
    if (code != null) {
      // Send the code to the server or process it as needed
      print('Received code: $code');
      // Rest of your code logic...
    }

    //print('Access Token: $result');
    */*/

