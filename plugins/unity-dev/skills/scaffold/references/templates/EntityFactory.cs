using Game.Core;
using Game.Data;
using UnityEngine;

namespace Game.Entities
{
    public static class {Name}Factory
    {
        public static {Name}Controller Create({Name}Data data, Vector3 position, Quaternion rotation)
        {
            // Human setup required:
            // 1. Create {Name}.prefab in Unity Editor
            // 2. Attach {Name}Controller component to prefab
            // 3. Place prefab in Resources/{Name} folder

            var prefab = Resources.Load<GameObject>("{Name}/{Name}");
            if (prefab == null)
            {
                Debug.LogError("Failed to load {Name} prefab. Human: ensure prefab exists at Resources/{Name}/{Name}.prefab");
                return null;
            }

            var instance = Object.Instantiate(prefab, position, rotation);
            var controller = instance.GetComponent<{Name}Controller>();
            controller.Init(data);
            return controller;
        }
    }
}
