"""Tests for utils.py."""

import logging
import textwrap


from pytype import debug
from pytype.pytd import cfg as typegraph

import unittest


log = logging.getLogger(__name__)


class Node(object):
  """A graph node, for testing topological sorting."""

  def __init__(self, name, *incoming):
    self.name = name
    self.outgoing = []
    self.incoming = list(incoming)
    for n in incoming:
      n.outgoing.append(self)

  def connect_to(self, other_node):
    self.outgoing.append(other_node)
    other_node.incoming.append(self)

  def __repr__(self):
    return "Node(%s)" % self.name


class DebugTest(unittest.TestCase):

  def setUp(self):
    self.prog = typegraph.Program()
    self.current_location = self.prog.NewCFGNode()

  def testAsciiTree(self):
    n1 = Node("n1")
    n2 = Node("n2", n1)
    n3 = Node("n3", n2)
    n4 = Node("n4", n3)
    n5 = Node("n5", n1)
    n6 = Node("n6", n5)
    n7 = Node("n7", n5)
    del n4, n6  # make pylint happy
    s = debug.ascii_tree(n1, lambda n: n.outgoing)
    self.assertMultiLineEqual(textwrap.dedent("""\
      Node(n1)
      |
      +-Node(n2)
      | |
      | +-Node(n3)
      |   |
      |   +-Node(n4)
      |
      +-Node(n5)
        |
        +-Node(n6)
        |
        +-Node(n7)
    """), s)
    s = debug.ascii_tree(n7, lambda n: n.incoming)
    self.assertMultiLineEqual(textwrap.dedent("""\
      Node(n7)
      |
      +-Node(n5)
        |
        +-Node(n1)
    """), s)

  def testAsciiGraph(self):
    n1 = Node("n1")
    n2 = Node("n2", n1)
    n3 = Node("n3", n2)
    n3.connect_to(n1)
    s = debug.ascii_tree(n1, lambda n: n.outgoing)
    self.assertMultiLineEqual(textwrap.dedent("""\
      Node(n1)
      |
      +-Node(n2)
        |
        +-Node(n3)
          |
          +-[Node(n1)]
    """), s)

  def testAsciiGraphWithCustomText(self):
    n1 = Node("n1")
    n2 = Node("n2", n1)
    n3 = Node("n3", n2)
    n3.connect_to(n1)
    s = debug.ascii_tree(n1, lambda n: n.outgoing, lambda n: n.name.upper())
    self.assertMultiLineEqual(textwrap.dedent("""\
      N1
      |
      +-N2
        |
        +-N3
          |
          +-[N1]
    """), s)

  def testTraceLogLevel(self):
    log.trace("hello world")


if __name__ == "__main__":
  unittest.main()
