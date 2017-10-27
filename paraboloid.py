def f(x, y, a, b, c):
    z = a*x**2+b*y**2+c*x*y
    z[z > 10] = np.nan
    z[z < -10] = np.nan
    return z

class Paraboloid(HasTraits):
    a = Range(-5., 5., 1)
    b = Range(-5., 5., 1)
    c = Range(-5., 5., 0)
    scene = Instance(MlabSceneModel, ())

    def __init__(self):
        # Do not forget to call the parent's __init__
        HasTraits.__init__(self)
        x, y = np.mgrid[-5:5:150j, -5:5:150j]
        self.plot = self.scene.mlab.surf(x, y, f(x, y, self.a, self.b, self.c))

    @on_trait_change('a,b,c,scene.activated')
    def update_plot(self):
        self.scene.mlab.axes(nb_labels=5)
        x, y = np.mgrid[-5:5:150j, -5:5:150j]
        self.plot.mlab_source.set(x=x, y=y, scalars=f(x, y, self.a, self.b, self.c))


    # the layout of the dialog created
    view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                    height=250, width=300, show_label=False),
                HGroup(
                        '_', 'a', 'b', 'c',
                    ),
                resizable=True,
                title="HELLO"
                )
