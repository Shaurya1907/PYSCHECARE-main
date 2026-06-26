const flashcardsData = [
  {
    id: 'welcome',
    title: 'Welcome',
    text: 'Welcome to the 5-4-3-2-1 grounding exercise. This technique will help you focus on the present moment and calm your mind.',
    icon: 'fa-spa'
  },
  {
    id: 'see',
    title: '5 Things You Can See',
    text: 'Look around you and name 5 things you can see. Notice their colors, shapes, and details.',
    icon: 'fa-eye'
  },
  {
    id: 'touch',
    title: '4 Things You Can Touch',
    text: 'Pay attention to your body and name 4 things you can feel. It could be the ground under your feet, or the texture of your clothes.',
    icon: 'fa-hand-paper'
  },
  {
    id: 'hear',
    title: '3 Things You Can Hear',
    text: 'Listen carefully to your surroundings. Name 3 things you can hear, whether they are close by or far away.',
    icon: 'fa-ear-listen'
  },
  {
    id: 'smell',
    title: '2 Things You Can Smell',
    text: 'Take a gentle breath in. Name 2 things you can smell right now. If you can\'t smell anything, imagine your favorite scent.',
    icon: 'fa-wind'
  },
  {
    id: 'taste',
    title: '1 Thing You Can Taste',
    text: 'Focus on your mouth. Name 1 thing you can taste. It might be a lingering flavor from a meal, a mint, or just the natural taste of your mouth.',
    icon: 'fa-utensils'
  },
  {
    id: 'complete',
    title: 'Great Job!',
    text: 'You have completed the grounding exercise. Take a deep breath. You are safe and grounded.',
    icon: 'fa-check-circle'
  }
];

const GroundingFlashcards = () => {
  const [currentIndex, setCurrentIndex] = React.useState(0);
  const [touchStart, setTouchStart] = React.useState(null);
  const [touchEnd, setTouchEnd] = React.useState(null);
  const [animationDirection, setAnimationDirection] = React.useState('');

  const minSwipeDistance = 50;

  const nextCard = () => {
    if (currentIndex < flashcardsData.length - 1) {
      setAnimationDirection('slide-left');
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const prevCard = () => {
    if (currentIndex > 0) {
      setAnimationDirection('slide-right');
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const restart = () => {
    setAnimationDirection('fade');
    setCurrentIndex(0);
  };

  const onTouchStart = (e) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const onTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > minSwipeDistance;
    const isRightSwipe = distance < -minSwipeDistance;

    if (isLeftSwipe) {
      nextCard();
    }
    if (isRightSwipe) {
      prevCard();
    }
  };

  React.useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowRight') {
        nextCard();
      } else if (e.key === 'ArrowLeft') {
        prevCard();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex]);

  const currentCard = flashcardsData[currentIndex];

  return (
    <div 
      className="flashcards-container"
      onTouchStart={onTouchStart}
      onTouchMove={onTouchMove}
      onTouchEnd={onTouchEnd}
      aria-label="Grounding Exercise Flashcards"
    >
      <div className="flashcards-progress" aria-live="polite">
        Card {currentIndex + 1} of {flashcardsData.length}
      </div>

      <div className="flashcards-progress-bar">
        <div 
          className="flashcards-progress-fill" 
          style={{ width: `${((currentIndex + 1) / flashcardsData.length) * 100}%` }}
        ></div>
      </div>

      <div className={`flashcard ${animationDirection}`} key={currentCard.id} tabIndex="0">
        <div className="flashcard-icon">
          <i className={`fas ${currentCard.icon}`}></i>
        </div>
        <h3 className="flashcard-title">{currentCard.title}</h3>
        <p className="flashcard-text">{currentCard.text}</p>
      </div>

      <div className="flashcards-controls">
        <button 
          onClick={prevCard} 
          disabled={currentIndex === 0}
          className="flashcard-btn prev-btn"
          aria-label="Previous card"
        >
          <i className="fas fa-chevron-left"></i> Previous
        </button>
        
        {currentIndex === flashcardsData.length - 1 ? (
          <button 
            onClick={restart} 
            className="flashcard-btn restart-btn"
            aria-label="Restart exercise"
          >
            <i className="fas fa-redo"></i> Restart
          </button>
        ) : (
          <button 
            onClick={nextCard} 
            className="flashcard-btn next-btn"
            aria-label="Next card"
          >
            Next <i className="fas fa-chevron-right"></i>
          </button>
        )}
      </div>
    </div>
  );
};

const rootNode = document.getElementById('grounding-flashcards-root');
if (rootNode) {
  const root = ReactDOM.createRoot(rootNode);
  root.render(<GroundingFlashcards />);
}
