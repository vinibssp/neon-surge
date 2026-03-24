from __future__ import annotations

import math
import random

from pygame import Vector2

from game.behaviors.advanced_helpers import normalized
from game.behaviors.behavior import Behavior
from game.components.data_components import CollisionComponent, MovementComponent, TransformComponent
from game.ecs.entity import Entity
from game.systems.world_queries import ENEMY_TRANSFORM_QUERY


class BouncerBehavior(Behavior):
    def update(self, entity: Entity, world: "GameWorld", dt: float) -> None:
        del dt
        transform = entity.get_component(TransformComponent)
        movement = entity.get_component(MovementComponent)
        collision = entity.get_component(CollisionComponent)
        if transform is None or movement is None or collision is None:
            return

        if movement.velocity.length_squared() <= 0:
            angle = random.uniform(0.0, math.pi * 2.0)
            movement.velocity = Vector2(math.cos(angle), math.sin(angle)) * max(1.0, movement.max_speed)

        normal = Vector2()
        if transform.position.x <= collision.radius:
            transform.position.x = collision.radius
            normal = Vector2(1, 0)
        elif transform.position.x >= world.width - collision.radius:
            transform.position.x = world.width - collision.radius
            normal = Vector2(-1, 0)

        if transform.position.y <= collision.radius:
            transform.position.y = collision.radius
            normal = Vector2(0, 1)
        elif transform.position.y >= world.height - collision.radius:
            transform.position.y = world.height - collision.radius
            normal = Vector2(0, -1)

        if normal.length_squared() > 0:
            movement.velocity = movement.velocity.reflect(normal)

        for neighbor in world.query(ENEMY_TRANSFORM_QUERY):
            if neighbor is entity:
                continue
            neighbor_transform = neighbor.get_component(TransformComponent)
            neighbor_collision = neighbor.get_component(CollisionComponent)
            if neighbor_transform is None or neighbor_collision is None:
                continue
            delta = transform.position - neighbor_transform.position
            distance = delta.length()
            safe_distance = collision.radius + neighbor_collision.radius + 5.0
            if distance <= 0 or distance >= safe_distance:
                continue
            reflection_normal = normalized(delta)
            movement.velocity = movement.velocity.reflect(reflection_normal)
            transform.position += reflection_normal * 3.0

        movement.input_direction = normalized(movement.velocity)
        movement.max_speed = max(1.0, movement.velocity.length())


from game.core.world import GameWorld
