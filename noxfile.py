import nox


@nox.session(python=["3.8"])
def sphinx(session):
    session.run("pip", "install", "sphinx", "sphinx_rtd_theme")
    session.run("pip", "install", "-r", "requirements.txt")
    session.run("python", "-m", "sphinx.cmd.build", "docs/source", "docs/build", "-b", "html")
