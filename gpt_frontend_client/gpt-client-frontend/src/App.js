import logo from './image.png';
import './normalize.css';
import './App.css';

function App() {
  return (
    <div className="App">
      <aside className="sideMenu">
        <div className="sideMenuButton">
          +   Yeni LiterAI
        </div>
      </aside>

      <section className="chatBox">
        <div className='chatLog'>

          <div className='chatMessage'>
            <div className='chatMessageAligner'>
              <div className='avatar'>
              </div>
              <div className='message'>
                Yatirim tavsiyesi verir misin
              </div>
            </div>          
          </div>

          <div className='chatMessageGpt4'>
            <div className='chatMessageAligner'>
              <div className='avatarGpt'>
              </div>
              <div className='message'>
                Evi satip Denizbank hissesi al -Rengin
              </div>
            </div>          
          </div>

        </div>

        <div className="chatInputBar">
          <textarea className="ChatInputWriteHere"
            rows="1"
            placeholder="Buraya Yazabilirsiniz">
          </textarea>
        </div>
        <p className="warningMessage">
          LiterAI bir Finnovator botudur ve hata yapabilir!
        </p>
      </section>
    </div>
  );
}

export default App;
