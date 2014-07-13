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
Jack Amadeo, the creator of this project, has not decided yet. Please bother him about this.
