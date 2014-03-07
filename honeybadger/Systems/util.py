def remove_dead(ent_set):
    dead = set()
    for e in ent_set:
        if e.is_dead:
            dead.add(e)
    ent_set.difference_update(dead)
