import pytest
from .example import rand


@pytest.mark.asyncio
async def test_rand_greater_zero():
    assert await rand() > 0.0
    
