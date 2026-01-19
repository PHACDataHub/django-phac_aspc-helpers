from phac_aspc.jinja.standard_helpers import cls_str


def test_cls_str():
    assert cls_str() == ""
    assert cls_str("class1") == " class1 "
    assert cls_str("class1", "class2") == " class1 class2 "
    assert cls_str("class1", "class2", "class3") == " class1 class2 class3 "
    assert cls_str("class1", None, "class3") == " class1 class3 "
    assert cls_str(None, None) == ""
    assert cls_str(None, "class2", None) == " class2 "

    assert cls_str(x=True, y=False) == " x "
    assert cls_str(x=False, y=True) == " y "
    assert cls_str("class1", x=True, y=True) == " class1 x y "

    assert cls_str("class1" and False, True and "class2") == " class2 "
    assert cls_str("class1" if False else "class2") == " class2 "
