from __future__ import annotations

import unittest

from pygame import Vector2

from game.components.data_components import CollisionComponent, StaggeredComponent, TransformComponent
from game.core.world import GameWorld
from game.ecs.entity import Entity
from game.ecs.query import WorldQuery


class ECSQueryWorldTest(unittest.TestCase):
    def test_world_query_filters_components_tags_and_predicate(self) -> None:
        e1 = Entity()
        e1.add_tag("enemy")
        e1.add_component(TransformComponent(position=Vector2(10, 20)))
        e1.add_component(CollisionComponent(radius=5, layer="enemy"))

        e2 = Entity()
        e2.add_tag("enemy")
        e2.add_tag("boss")
        e2.add_component(TransformComponent(position=Vector2(30, 40)))
        e2.add_component(CollisionComponent(radius=9, layer="enemy"))

        e3 = Entity()
        e3.active = False
        e3.add_tag("enemy")
        e3.add_component(TransformComponent(position=Vector2(50, 60)))
        e3.add_component(CollisionComponent(radius=3, layer="enemy"))

        query = WorldQuery(
            component_types=(TransformComponent, CollisionComponent),
            tags=("enemy",),
            excluded_tags=("boss",),
            predicate=lambda entity: (entity.get_component(CollisionComponent) or CollisionComponent(0, "")).radius >= 5,
        )

        matched = query.filter([e1, e2, e3])

        self.assertEqual([entity.id for entity in matched], [e1.id])

    def test_query_include_inactive_true_allows_inactive_entities(self) -> None:
        e = Entity()
        e.active = False
        e.add_tag("enemy")

        query = WorldQuery(tags=("enemy",), include_inactive=True)
        self.assertEqual(query.filter([e]), [e])

    def test_game_world_add_enemy_applies_spawn_freeze_component(self) -> None:
        world = GameWorld(width=100, height=100)
        enemy = Entity()
        enemy.add_tag("enemy")

        world.add_entity(enemy)
        world.apply_pending()

        stagger = enemy.get_component(StaggeredComponent)
        self.assertIsNotNone(stagger)
        assert stagger is not None
        self.assertGreater(stagger.time_left, 0.0)

    def test_game_world_query_and_remove_pending(self) -> None:
        world = GameWorld(width=100, height=100)
        entity = Entity()
        entity.add_tag("enemy")
        world.add_entity(entity)
        world.apply_pending()

        matched_before = world.query(WorldQuery(tags=("enemy",)))
        self.assertEqual(matched_before, [entity])

        world.remove_entity(entity)
        world.apply_pending()

        matched_after = world.query(WorldQuery(tags=("enemy",)))
        self.assertEqual(matched_after, [])


if __name__ == "__main__":
    unittest.main()
