traintime
=========

A prototype web app for fetching NYC MTA real-time train status.


To Contribute
=============
* Step 0: Fork + clone project here on Github.
* Step 1: Download and install the Google app engine, located here: https://developers.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python
* Step 2: Register for your own MTA API key here: http://datamine.mta.info/user/register
* Step 3: Place the key in a file in the project root like this: ./traintime/mta_api_key, and store it in JSON that looks like this:

  {
    "api_key" : "YOUR_API_KEY_HERE"
  }

* Step 4: Run the traintime/compile_templates.sh
* Step 5: Add the project directory to GAE (Google App Engine installed above)
* Step 6: Hit the play button. The server should now be accessible on localhost:8080

LICENSE
=======
Copyright (c) 2014 Jack Amadeo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
