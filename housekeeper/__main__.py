from housekeeper import core

if __name__ == '__main__':
    core = core.Core()
    core.load_plugin('anycheck')
    core.load_plugin('backgroundchanger')
    core.load_plugin('powercontrol')
    core.load_plugin('sync')
    core.execute_from_command_line()
