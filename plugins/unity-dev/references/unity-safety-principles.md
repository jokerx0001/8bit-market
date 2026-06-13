# Unity AI-Safe Development Principles

## The Three Golden Rules

1. **AI must NOT touch Scene / Prefab / Animator** — these are human-editor systems
2. **All logic must be code-centralized** — not scattered across Inspector + events + Animator + Timeline
3. **Single entry-point systems** — AI only modifies the System layer, never object state directly

---

## Principle 1: Game State Machine — AI Controls Flow Exclusively Through It

**Wrong:**
```csharp
if (player.hp <= 0) Destroy(player);
```

**Correct:**
```csharp
GameStateMachine.Transition(GameState.GameOver);
```

The State Machine enforces a single choke point for all flow control. AI is prone to scattering condition checks everywhere, causing branch explosion and state inconsistency.

---

## Principle 2: Event Bus — No Direct Cross-System References

**Wrong (AI's instinct):**
```csharp
enemy.TakeDamage(player.attack);
ui.UpdateHP();
audio.PlayHit();
```

**Correct:**
```csharp
EventBus.Publish(new DamageEvent(targetId, 10));
```

CombatSystem handles damage, UISystem listens for UI updates, AudioSystem plays sounds. AI cannot randomly call other systems. Logic changes don't cascade.

---

## Principle 3: ScriptableObject = Data Only, No Logic

**Wrong:**
```csharp
// Logic inside SO, or SO calling functions
public class WeaponData : ScriptableObject {
    public void Fire() { ... }
}
```

**Correct:**
```csharp
[CreateAssetMenu]
public class WeaponData : ScriptableObject
{
    public float damage;
    public float fireRate;
    public float recoil;
}
```

ScriptableObject = Excel spreadsheet, not a program.

---

## Principle 4: No Direct Prefab Manipulation by AI

**Forbidden:** AI modifying prefab hierarchy, animator controller, or scenes.

**Alternative — Factory + Config pattern:**
```csharp
var enemy = EnemyFactory.Create(enemyType);
enemy.Init(enemyData);
```

AI only writes code. Scene structure stays intact. Rollback is possible.

---

## Principle 5: Stateless or Single-Direction State

**Wrong:** Boolean flags scattered everywhere, mutual state references, state sync hell.

**Correct:** State exists in exactly one place:
```csharp
PlayerState { hp, stamina, position }
```

Other systems can only **read** or **request modification** — never modify directly.

---

## Principle 6: No Direct Unity Component Manipulation

**Forbidden:**
```csharp
transform.position = ...
GetComponent<Rigidbody>().velocity = ...
```

**Correct:**
```csharp
movement.MoveTo(target);
combat.ApplyDamage(10);
```

Unity components are implicit-state hell. AI cannot trace the impact chain.

---

## Principle 7: Logging + Observability

Required infrastructure:
1. **System Log**: `Log.Event("DamageApplied", data);`
2. **State Dump**: `Debug.Dump(GameState);`
3. **Event Trace**: `PlayerAttack → DamageEvent → EnemyHealth → UIUpdate`

AI fears black-box systems. Transparency is mandatory.

---

## AI Permissions Matrix

### FORBIDDEN for AI:
- Modifying Scene files (.unity)
- Modifying Prefab structure
- Modifying Animator / Animation
- Direct Unity component manipulation (transform, Rigidbody, etc.)
- Cross-system direct method calls
- Scattering boolean state flags

### ALLOWED for AI:
- C# logic code
- ScriptableObject data fields
- System-layer code (Systems/)
- Event definitions (new event types)
- Factory code
- Unit tests

---

## Recommended Project Architecture

```
/Game
  /Core
    GameManager         — Singleton entry point
    GameStateMachine    — Flow control
    EventBus            — Pub/sub messaging
  /Systems
    PlayerSystem        — Player-specific logic
    EnemySystem         — Enemy-specific logic
    CombatSystem        — Damage/combat resolution
    InventorySystem     — Item management
  /Data
    ScriptableObjects   — Pure data assets (no logic)
  /View
    UIController        — UI updates via events
    VFXController       — Visual effects via events
  /Entities
    PlayerController    — Player entity behavior
    EnemyController     — Enemy entity behavior
```

## Human Responsibilities (must remind user)

When AI generates code, the human MUST handle:
1. Creating/editing Prefabs in Unity Editor
2. Wiring up Scene references
3. Configuring Animator Controllers
4. Assigning ScriptableObject data in Inspector
5. Setting up Unity project settings
