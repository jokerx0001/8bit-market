using System;
using System.Collections.Generic;

namespace Game.Core
{
    public static class EventBus
    {
        private static readonly Dictionary<Type, List<Delegate>> Subscribers = new();

        public static void Initialize()
        {
            Subscribers.Clear();
        }

        public static void Subscribe<T>(Action<T> handler) where T : IGameEvent
        {
            var type = typeof(T);
            if (!Subscribers.ContainsKey(type))
                Subscribers[type] = new List<Delegate>();
            Subscribers[type].Add(handler);
        }

        public static void Unsubscribe<T>(Action<T> handler) where T : IGameEvent
        {
            var type = typeof(T);
            if (Subscribers.ContainsKey(type))
                Subscribers[type].Remove(handler);
        }

        public static void Publish<T>(T gameEvent) where T : IGameEvent
        {
            var type = typeof(T);
            if (!Subscribers.ContainsKey(type)) return;

            foreach (var handler in Subscribers[type])
            {
                ((Action<T>)handler)?.Invoke(gameEvent);
            }

            Log.Event(typeof(T).Name, gameEvent);
        }

        public static void Dispose()
        {
            Subscribers.Clear();
        }
    }
}
