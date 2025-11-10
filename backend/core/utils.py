def xp_to_next_level(level: int) -> int:
    # простая формула: каждые 100 * уровень XP
    return 100 * level

def add_xp(user, amount: int, db):
    user.xp += amount
    needed = xp_to_next_level(user.level)
    while user.xp >= needed:
        user.xp -= needed
        user.level += 1
        needed = xp_to_next_level(user.level)
    db.commit()
