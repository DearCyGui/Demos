from demo_utils import documented, democode, push_group, pop_group, launch_demo, demosection
import dearcygui as dcg

push_group("Intro")
import intro
pop_group()
push_group("Basics")
import basics
pop_group()
push_group("Widgets")
import widgets
pop_group()
push_group("Tables")
import tables
pop_group()
push_group("Plots")
import plots
pop_group()
push_group("Drawings")
import drawings
pop_group()
push_group("Styles")
import styles
pop_group()
push_group("Subclassing")
import subclassing
pop_group()
push_group("Advanced")
import advanced
pop_group()

if __name__ == "__main__":
    launch_demo(title="Dearcygui Demo")