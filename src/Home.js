import * as script from "./script.js"

function Home() {
  debugger;
  script.doShit();
  return (
    <div>
      <h1>Spotify Skipper</h1>
      <script src="src/script.js" type="module"></script>
      <section id="profile">
        <h2>Logged in as <span id="displayName"></span></h2>
        <img id="avatar" width="200" src="#" />
        <ul>
          <li>User ID: <span id="id"></span></li>
          <li>Email: <span id="email"></span></li>
          <li>Spotify URI: <a id="uri" href="#"></a></li>
          <li>Link: <a id="url" href="#"></a></li>
          <li>Profile Image: <span id="imgUrl"></span></li>
        </ul>
      </section>
    </div>
  );
  }
  
  export default Home;
  