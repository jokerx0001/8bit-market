using Game.Core;
using UnityEngine;

namespace Game.Entities
{
    public class {Name}Controller : MonoBehaviour
    {
        private {Name}Data _data;

        public void Init({Name}Data data)
        {
            _data = data;
        }

        // Entity behavior methods — never directly manipulate transform/rigidbody here
        // Use dedicated component wrappers or call System-layer methods via EventBus
    }
}
