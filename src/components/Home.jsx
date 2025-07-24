import './Home.css';

const Home = ({ setView }) => {
  return (
    <div className="home-container">
      <header className="home-header">
        <h1 className="main-heading">Let's Do DSA Together 🚀</h1>
        <p className="sub-heading">
          Your one-stop guide to mastering Data Structures & Algorithms. From basics to advanced, all in one place.
        </p>
      </header>

      <section className="cards-section">
        <div className="card beginner">
          <h2>Beginner</h2>
          <p>Start your DSA journey with handpicked beginner-level problems and concepts explained simply.</p>
          <button onClick={() => setView('beginner')}>Explore Beginner</button>
        </div>

        <div className="card advanced">
          <h2>Advanced</h2>
          <p>Take your skills up a notch. Dive into complex patterns, DP, graphs, and real interview problems.</p>
          <button onClick={() => setView('advanced')}>Explore Advanced</button>
        </div>

        <div className="card both">
          <h2>All-in-One</h2>
          <p>Don't want to choose? Explore everything from beginner to advanced in a guided roadmap format.</p>
          <button onClick={() => setView('beginner')}>Start Full Journey</button>
        </div>
      </section>

      <footer className="home-footer">
        <p>Made with ❤️ for aspiring developers</p>
        <p>© 2025 Let's Do DSA</p>
      </footer>
    </div>
  );
};

export default Home;
