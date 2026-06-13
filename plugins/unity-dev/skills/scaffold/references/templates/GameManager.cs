using UnityEngine;

namespace Game.Core
{
    public class GameManager : MonoBehaviour
    {
        public static GameManager Instance { get; private set; }

        [SerializeField] private GameState initialState = GameState.Menu;

        private void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(gameObject);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);

            GameStateMachine.Initialize(initialState);
            EventBus.Initialize();
        }

        private void Start()
        {
            GameStateMachine.Transition(initialState);
        }

        private void OnDestroy()
        {
            if (Instance == this)
            {
                EventBus.Dispose();
                Instance = null;
            }
        }
    }
}
