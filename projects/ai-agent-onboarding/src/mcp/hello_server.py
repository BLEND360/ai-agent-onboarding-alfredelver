from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("hello-world")


@mcp.tool()
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}! "


@mcp.tool()
def add(a: float, b: float) -> str:
    """Add two numbers"""
    return f"{a}+{b} = {a+b}"


if __name__ == "__main__":
    mcp.run()
