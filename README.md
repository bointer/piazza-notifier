# Piazza Notifier

Simple web application for sending emails to subscribers when a new resource is posted to [Piazza](https://piazza.com).

This application consists of:
- A web page "client" built using [Vue.js](https://vuejs.org),
- A [Python](https://python.org) "server" script that emails subscribers, and
- A [Firebase](https://firebase.google.com) instance to handle authentication

The server uses a local SMTP server (i.e., `sendmail`) to send emails to subscribers.

## Setup

### Prerequisites
- [Node.js](https://nodejs.org/)
- [Yarn](https://yarnpkg.com)
- [Python3](https://www.python.org)

### Firebase
Create a [Firebase project](https://console.firebase.google.com). Under Authentication, make sure to enable the **Email/Password** sign-in method, as well as **Email link (passwordless sign-in)**.

Next, create a new **Web app** in the Project Overview. Once the app is created, go to Project Settings and copy the **Firebase SDK snippet** with the "Config" option. Add the `export` keyword right before the variable. It should look something like this:

```javascript
export const firebaseConfig = {
  apiKey: "xxx",
  authDomain: "xxx",
  projectId: "xxx",
  storageBucket: "xxx",
  messagingSenderId: "xxx",
  appId: "xxx"
};
```

Save this to a file named `firebase.js` inside the `web/src` directory.

Lastly, under Service Accounts in Project Settings, generate a new private key for the application. Keep ahold of this; it will be used when setting up the server.

### Server
First, install the dependencies:
```bash
pip3 install -r requirements.txt
```
Then, make a copy of [env.template](env.template) and name it `env.py`.

- Fill in the `PIAZZA_USER` and `PIAZZA_PASS` fields with your credentials.
- `COURSE_NAME` is just a simple name for your course (e.g, 'CS101').
- `COURSE_NID` is the "network ID" of the course on Piazza. This can be found by copying the last section of the URL to your course Q&A page (i.e., the part after `/class/`).
- `RESOURCES_URL` is just the URL of the course Resources page.
- `SENDER_NAME` will be the name attached to the emails the program sends.
- Likewise, `SENDER_EMAIL` is the email to send from.
- `CHECK_FREQUENCY` should be set to how many minutes will pass between invocations of the script.
- `FIREBASE_CREDENTIALS` should be a path to where you saved the Firebase service account private key.
- `UNSUBSCRIBE_URL` should be a link to where the client is deployed. This will be displayed at the end of each email.

The `DEV` field determines if emails are actually sent. When it is `True`, email contents will be printed to the console. When it is `False`, emails will be sent using `sendmail`.

You can now run the server:
```bash
python3 main.py
```

### Client
The client app is located in the `web/` subdirectory.

First, install the dependencies:
```bash
yarn install
```

Next, set the variables inside of `web/.env` to match your use case. `PUBLIC_PATH` should be set to the folder path where you will deploy the application.

You can now run the development server for the client:
```bash
yarn serve
```

Once you are ready to deploy, build the app:
```bash
yarn build
```

The built files will be inside the `web/dist` folder. Copy the contents of this folder to the server you are deploying to.

## License

Licensed under the [MIT License](LICENSE).
