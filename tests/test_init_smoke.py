def test_import_modelcub_exposes_events():
    import modelcub
    assert hasattr(modelcub, "events")
