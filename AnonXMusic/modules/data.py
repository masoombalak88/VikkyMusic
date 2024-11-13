from .core import mongodb
from typing import Dict, List, Union


gdeldb = mongodb.gdel


# Global Delete
async def get_gdel_user() -> list:
    results = []
    async for user in gdeldb.find({"user_id": {"$gt": 0}}):
        user_id = user["user_id"]
        results.append(user_id)
    return results


async def get_gdel_count() -> int:
    users = gdeldb.find({"user_id": {"$gt": 0}})
    users = await users.to_list(length=100000)
    return len(users)


async def is_gdel_user(user_id: int) -> bool:
    user = await gdeldb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def add_gdel_user(user_id: int):
    is_gdel = await is_gdel_user(user_id)
    if is_gdel:
        return
    return await gdeldb.insert_one({"user_id": user_id})


async def del_gdel_user(user_id: int):
    is_gdel = await is_gdel_user(user_id)
    if not is_gdel:
        return
    return await gdeldb.delete_one({"user_id": user_id})
  
