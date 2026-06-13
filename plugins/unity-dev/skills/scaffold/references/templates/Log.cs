using UnityEngine;

namespace Game.Core
{
    public static class Log
    {
        public static void Event(string eventName, object data = null)
        {
            var json = data != null ? JsonUtility.ToJson(data) : "{}";
            Debug.Log($"[EVENT] {eventName} | {json}");
        }

        public static void StateDump(object state)
        {
            var json = JsonUtility.ToJson(state, true);
            Debug.Log($"[STATE DUMP]\n{json}");
        }

        public static void Trace(string chain)
        {
            Debug.Log($"[TRACE] {chain}");
        }
    }
}
