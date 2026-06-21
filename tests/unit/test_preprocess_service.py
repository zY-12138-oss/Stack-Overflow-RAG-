from app.services.preprocess_service import PreprocessService


def test_preprocess_detects_zh_language() -> None:
    service = PreprocessService()

    result = service.process("Redis 批量写入后反序列化报错怎么办")

    assert result["language"] == "zh"
    assert "Redis" in result["keywords"]
