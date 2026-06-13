using System;
using System.Collections.Generic;
using UnityEngine;

namespace Game.Core
{
    public enum GameState
    {
        Menu,
        Loading,
        Playing,
        Paused,
        GameOver
    }

    public static class GameStateMachine
    {
        public static GameState CurrentState { get; private set; }
        public static GameState PreviousState { get; private set; }

        private static readonly Dictionary<GameState, List<Action>> EnterCallbacks = new();
        private static readonly Dictionary<GameState, List<Action>> ExitCallbacks = new();

        public static void Initialize(GameState initialState)
        {
            CurrentState = initialState;
            PreviousState = initialState;

            foreach (GameState state in Enum.GetValues(typeof(GameState)))
            {
                EnterCallbacks[state] = new List<Action>();
                ExitCallbacks[state] = new List<Action>();
            }
        }

        public static void Transition(GameState newState)
        {
            if (newState == CurrentState) return;

            foreach (var callback in ExitCallbacks[CurrentState])
                callback?.Invoke();

            PreviousState = CurrentState;
            CurrentState = newState;

            foreach (var callback in EnterCallbacks[newState])
                callback?.Invoke();

            Log.Event("StateChanged", new { PreviousState, CurrentState });
        }

        public static void OnEnter(GameState state, Action callback)
        {
            EnterCallbacks[state].Add(callback);
        }

        public static void OnExit(GameState state, Action callback)
        {
            ExitCallbacks[state].Add(callback);
        }
    }
}
