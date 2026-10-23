import importlib.util
import json
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('ikea_importer',Path(__file__).resolve().parents[1]/'scripts/import-ikea.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def fixture(measures, **overrides):
    data={'@type':'Product','sku':'123.456.78','name':'TEST 테스트 의자 - 화이트','category':'사무용 의자',
          'offers':{'priceCurrency':'KRW','price':'89900','url':'https://www.ikea.com/kr/ko/p/test-12345678/'}}
    data.update(overrides)
    rows=''.join(f'<span class="pipf-measurements-tab__measurement-name">{label}</span><span class="pipf-measurements-tab__measurement-value">{value}</span>' for label,value in measures.items())
    return '<script type="application/ld+json">'+json.dumps(data)+'</script><p>전체 높이 120 cm 사용자 후기 시트 높이 99 cm</p>'+rows


class ImportTests(unittest.TestCase):
    def test_only_official_dimension_rows_are_used(self):
        product,_=module.parse_product(fixture({'최소 시트 높이':'40 cm','최대 시트 높이':'52 cm','시트 깊이':'39 cm','시트 폭':'40 cm'}),'12345678','chair')
        self.assertEqual(product['height'],[400,520]);self.assertEqual(product['depth'],[390,390])
        self.assertEqual(product['article'],'12345678')
    def test_missing_seat_data_never_uses_overall_height_or_reviews(self):
        product,_=module.parse_product(fixture({'높이':'120 cm'}),'12345678','chair')
        self.assertIsNone(product['height']);self.assertIsNone(product['depth']);self.assertEqual(product['heightStatus'],'missing')
    def test_foreign_prices_and_wrong_articles_are_rejected(self):
        with self.assertRaises(ValueError):module.parse_product(fixture({},offers={'priceCurrency':'USD','price':'10'}),'12345678','chair')
        with self.assertRaises(ValueError):module.product_schema(fixture({}),'87654321')
    def test_chair_parts_are_excluded(self):
        with self.assertRaises(ValueError):module.parse_product(fixture({},name='TEST 테스트 의자 하부프레임 - 블랙'),'12345678','chair')

if __name__=='__main__':unittest.main()
