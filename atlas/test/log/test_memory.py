
from atlas.log import MemoryHandler, AttributeFormatter
import logging

def test_read(tmpdir):
    # TODO
    expected_records = [
        {"msg": "event 1", "extra": {"task_name": "mytask", "action": "run"}},
        {"msg": "event 1", "extra": {"task_name": "mytask", "action": "success"}},
    ]
    with tmpdir.as_cwd() as old_dir:
        logger = logging.getLogger("_test.test_types")
        handler = MemoryHandler("dict")
        handler.setFormatter(AttributeFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        for record in expected_records:
            logger.info(**record)

        actual_records = handler.read()
        #actual_records = list(records)
        for actual_record, expected_record in zip(actual_records, expected_records):
            extras = expected_record.pop("extra")

            # Test all basic items found
            assert expected_record.items() <= actual_record.items()

            # Test all extras found
            assert extras.items() <= actual_record.items()
