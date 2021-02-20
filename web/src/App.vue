<template>
  <div id="app">
    <h1>{{ courseName }} Piazza Mailing List</h1>

    <p class="info-message" v-show="infoMessage">{{ infoMessage }}</p>
    <p class="error-message" v-show="errorMessage">{{ errorMessage }}</p>

    <div v-if="user">
      <p>Hi, {{ user.email }}!</p>
      <br />
      <p><a href="#" @click="unsubscribe()">Unsubscribe</a></p>
    </div>
    <div v-else>
      <p>
        Subscribe to this mailing list to get notified whenever a new homework
        or set of lecture notes are posted to Piazza.
      </p>
      <br />

      <form @submit.prevent="sendSignInLink()">
        <label for="email">Your email:</label>
        <input
          type="email"
          id="email"
          v-model="email"
          placeholder="pete@purdue.edu"
          required
        />

        <input type="submit" name="subscribe" value="Subscribe" />
        <input type="submit" name="unsubscribe" value="Unsubscribe" />
      </form>
    </div>

    <p>
      This service is brought to you by
      <a href="https://github.com/drewdavis21">Andrew Davis</a>.<br />
      You can view the source code on
      <a href="https://github.com/drewdavis21/piazza-notifier">GitHub</a>.
    </p>
  </div>
</template>

<script>
import firebase from "firebase/app";
import "firebase/auth";

export default {
  name: "Home",
  created: function () {
    this.handleSignIn();

    firebase.auth().onAuthStateChanged((user) => {
      this.user = user;
      this.email = user.email;
    });
  },
  data: function () {
    return {
      courseName: process.env.VUE_APP_COURSE_NAME,
      email: "",
      user: firebase.auth().currentUser,
      infoMessage: undefined,
      errorMessage: undefined,
    };
  },
  methods: {
    sendSignInLink() {
      firebase
        .auth()
        .sendSignInLinkToEmail(this.email, {
          url: window.location.href,
          handleCodeInApp: true,
        })
        .then(() => {
          this.infoMessage =
            "Please verify your email using the link we just sent.";
          window.localStorage.setItem("userEmail", this.email);
        })
        .catch((error) => {
          console.error(error);
        });
    },
    handleSignIn() {
      if (firebase.auth().isSignInWithEmailLink(window.location.href)) {
        var email = window.localStorage.getItem("userEmail");
        if (!email) {
          email = window.prompt(
            "Please confirm the email you'd like to authenticate with."
          );
        }

        if (email) {
          firebase
            .auth()
            .signInWithEmailLink(email, window.location.href)
            .then(() => {
              window.localStorage.removeItem("userEmail");
              if (history && history.replaceState) {
                window.history.replaceState(
                  {},
                  document.title,
                  window.location.href.split("?")[0]
                );
              }
            })
            .catch((error) => {
              console.error(error);
            });
        }
      }
    },
    unsubscribe() {
      var confirmed = window.confirm("Are you sure you want to unsubscribe?");
      if (confirmed) {
        firebase
          .auth()
          .currentUser.delete()
          .then(() => {
            this.email = "";
            this.infoMessage =
              "You have been unsubscribed from the mailing list. Thanks for trying it out!";
          })
          .catch((error) => {
            if (error.code == "auth/requires-recent-login") {
              this.sendSignInLink();
            } else {
              console.error("ok" + error);
            }
          });
      }
    },
  },
};
</script>

<style lang="scss">
h1,
p,
form {
  text-align: center;
}

form * {
  margin: 0 0.2em;
}

.info-message {
  color: green;
}

.error-message {
  color: red;
}
</style>
