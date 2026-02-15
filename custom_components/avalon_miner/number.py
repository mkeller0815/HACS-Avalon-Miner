# number.py (root)
from .entities.number import async_setup_entry as setup_entities


async def async_setup_entry(hass, entry, async_add_entities):
    await setup_entities(hass, entry, async_add_entities)
