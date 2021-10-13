import obspython as obs

def setTransition(num):
    transitions = obs.obs_frontend_get_transitions()
    print(len(transitions))
    if num < len(transitions) and num >= 0:
        obs.obs_frontend_set_current_transition(transitions[num])
        
def transition(num = -1):
    trans = None
    if num >= 0 :
        setTransition(num)
    trans = obs.obs_frontend_get_current_transition()
    act = obs.obs_frontend_get_current_scene()
    mode = obs.OBS_TRANSITION_MODE_AUTO
    duration = 0
    dest = obs.obs_frontend_get_current_preview_scene()
    obs.obs_transition_start(trans, mode, duration, dest)
    obs.obs_frontend_set_current_scene(dest)
    obs.obs_frontend_set_current_preview_scene(act)

def setPreview(num):
    scenes = obs.obs_frontend_get_scenes()
    if num < len(scenes) and num >= 0:
        obs.obs_frontend_set_current_preview_scene(scenes[num])

sources = obs.obs_enum_sources()
for source in sources:
    name = obs.obs_source_get_name(source)
    print(name)
    settings = obs.obs_source_get_settings(source)
    json = obs.obs_data_get_json(settings)
    print(json)
