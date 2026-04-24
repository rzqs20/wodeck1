"""
Indicator Service 测试程序
测试指标管理服务的各项功能
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def init_database():
    """初始化数据库表结构"""
    from config.database import create_engine_instance
    from models.indicator import Indicator
    
    engine = create_engine_instance()
    
    print("正在初始化数据库表...")
    Indicator.__table__.create(engine, checkfirst=True)
    print("✅ 数据库表初始化完成")


def test_create_indicator():
    """测试创建指标"""
    print_section("测试1: 创建指标")
    
    from services.indicator_service import create_indicator
    
    try:
        # 测试1.1: 创建基本指标
        print("测试1.1: 创建基本指标")
        indicator = create_indicator(
            name='测试MA',
            description='测试用移动平均线',
            formula='MA(CLOSE, N)',
            parameters={'N': 10},
            category='custom'
        )
        
        print(f"   ✅ 创建成功，ID: {indicator.id}")
        print(f"   名称: {indicator.name}")
        print(f"   公式: {indicator.formula}")
        assert indicator.id > 0, "ID应该大于0"
        assert indicator.name == '测试MA', "名称应该匹配"
        
        # 测试1.2: 创建不带公式的指标
        print("\n测试1.2: 创建不带公式的指标")
        indicator2 = create_indicator(
            name='简单指标',
            description='没有公式'
        )
        print(f"   ✅ 创建成功，ID: {indicator2.id}")
        
        # 测试1.3: 名称重复应该失败
        print("\n测试1.3: 名称重复检测")
        try:
            create_indicator(name='测试MA')
            print("   ❌ 应该抛出异常")
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
        # 测试1.4: 空名称应该失败
        print("\n测试1.4: 空名称检测")
        try:
            create_indicator(name='')
            print("   ❌ 应该抛出异常")
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
        # 测试1.5: 名称过长应该失败
        print("\n测试1.5: 名称长度检测")
        try:
            create_indicator(name='A' * 51)
            print("   ❌ 应该抛出异常")
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
        return indicator
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_validate_formula():
    """测试公式验证"""
    print_section("测试2: 公式验证")
    
    from services.indicator_service import validate_formula
    
    try:
        # 测试2.1: 合法公式
        print("测试2.1: 合法公式")
        valid_formulas = [
            'MA(CLOSE, 5)',
            'CLOSE + OPEN',
            'HIGH - LOW',
            'MACD(CLOSE, 12, 26, 9)',
            '(HIGH + LOW + CLOSE) / 3',
        ]
        
        for formula in valid_formulas:
            result = validate_formula(formula)
            print(f"   ✅ '{formula}' 验证通过")
            assert result == True
        
        # 测试2.2: 危险函数应该被拒绝
        print("\n测试2.2: 危险函数检测")
        dangerous_formulas = [
            ('eval("1+1")', 'eval'),
            ('exec("print(1)")', 'exec'),
            ('__import__("os")', '__import__'),
            ('open("/etc/passwd")', 'open'),
        ]
        
        for formula, func_name in dangerous_formulas:
            try:
                validate_formula(formula)
                print(f"   ❌ '{formula}' 应该被拒绝")
            except ValueError as e:
                print(f"   ✅ 正确拒绝 {func_name}: {e}")
        
        # 测试2.3: 语法错误应该被捕获
        print("\n测试2.3: 语法错误检测")
        invalid_formulas = [
            'MA(CLOSE,',  # 括号不匹配
            'CLOSE +',    # 运算符不完整
            'MA CLOSE 5', # 缺少括号
        ]
        
        for formula in invalid_formulas:
            try:
                validate_formula(formula)
                print(f"   ❌ '{formula}' 应该有语法错误")
            except ValueError as e:
                print(f"   ✅ 正确捕获语法错误: {str(e)[:50]}")
        
        # 测试2.4: 空公式应该失败
        print("\n测试2.4: 空公式检测")
        try:
            validate_formula('')
            print("   ❌ 应该抛出异常")
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_parse_parameters():
    """测试参数解析"""
    print_section("测试3: 参数解析")
    
    from services.indicator_service import parse_parameters
    
    try:
        # 测试3.1: 字典输入
        print("测试3.1: 字典输入")
        params = {'N': 10, 'M': 5}
        result = parse_parameters(params)
        print(f"   ✅ 字典解析: {result}")
        assert result == params
        
        # 测试3.2: JSON字符串输入
        print("\n测试3.2: JSON字符串输入")
        json_str = '{"N": 20, "P": 2}'
        result = parse_parameters(json_str)
        print(f"   ✅ JSON解析: {result}")
        assert result == {'N': 20, 'P': 2}
        
        # 测试3.3: 空字符串
        print("\n测试3.3: 空字符串")
        result = parse_parameters('')
        print(f"   ✅ 空字符串返回空字典: {result}")
        assert result == {}
        
        # 测试3.4: None
        print("\n测试3.4: None输入")
        result = parse_parameters(None)
        print(f"   ✅ None返回空字典: {result}")
        assert result == {}
        
        # 测试3.5: 无效JSON
        print("\n测试3.5: 无效JSON")
        try:
            parse_parameters('{invalid json}')
            print("   ❌ 应该抛出异常")
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
        # 测试3.6: 非字典类型
        print("\n测试3.6: 非字典类型")
        try:
            parse_parameters([1, 2, 3])
            print("   ❌ 应该抛出异常")
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_get_indicators():
    """测试查询指标"""
    print_section("测试4: 查询指标")
    
    from services.indicator_service import (
        get_indicator,
        get_indicator_by_name,
        get_all_indicators
    )
    
    try:
        # 先创建一些测试数据
        from services.indicator_service import create_indicator
        
        ind1 = create_indicator(name='指标A', formula='MA(CLOSE, 5)')
        ind2 = create_indicator(name='指标B', formula='RSI(CLOSE, 14)')
        ind3 = create_indicator(name='指标C', category='technical')
        
        print(f"创建了3个测试指标: {ind1.id}, {ind2.id}, {ind3.id}")
        
        # 测试4.1: 根据ID查询
        print("\n测试4.1: 根据ID查询")
        result = get_indicator(ind1.id)
        print(f"   ✅ 查询到: {result.name}")
        assert result.id == ind1.id
        assert result.name == '指标A'
        
        # 测试4.2: 查询不存在的ID
        print("\n测试4.2: 查询不存在的ID")
        result = get_indicator(99999)
        print(f"   ✅ 不存在返回: {result}")
        assert result is None
        
        # 测试4.3: 根据名称查询
        print("\n测试4.3: 根据名称查询")
        result = get_indicator_by_name('指标B')
        print(f"   ✅ 查询到: {result.name}")
        assert result.name == '指标B'
        
        # 测试4.4: 获取所有指标
        print("\n测试4.4: 获取所有指标")
        all_indicators = get_all_indicators()
        print(f"   ✅ 共有 {len(all_indicators)} 个指标")
        assert len(all_indicators) >= 3
        
        # 测试4.5: 按分类过滤
        print("\n测试4.5: 按分类过滤")
        technical = get_all_indicators(category='technical')
        print(f"   ✅ technical分类有 {len(technical)} 个指标")
        
        custom = get_all_indicators(category='custom')
        print(f"   ✅ custom分类有 {len(custom)} 个指标")
        
        # 清理测试数据
        from services.indicator_service import delete_indicator
        delete_indicator(ind1.id)
        delete_indicator(ind2.id)
        delete_indicator(ind3.id)
        print("\n   ✅ 测试数据已清理")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_update_indicator():
    """测试更新指标"""
    print_section("测试5: 更新指标")
    
    from services.indicator_service import (
        create_indicator,
        update_indicator,
        delete_indicator
    )
    
    try:
        # 创建测试指标
        indicator = create_indicator(
            name='待更新指标',
            description='原始描述',
            formula='MA(CLOSE, 5)',
            parameters={'N': 5}
        )
        print(f"创建指标 ID: {indicator.id}")
        
        # 测试5.1: 更新名称
        print("\n测试5.1: 更新名称")
        updated = update_indicator(indicator.id, {'name': '新名称'})
        print(f"   ✅ 名称更新为: {updated.name}")
        assert updated.name == '新名称'
        
        # 测试5.2: 更新描述
        print("\n测试5.2: 更新描述")
        updated = update_indicator(indicator.id, {'description': '新描述'})
        print(f"   ✅ 描述更新为: {updated.description}")
        assert updated.description == '新描述'
        
        # 测试5.3: 更新公式
        print("\n测试5.3: 更新公式")
        updated = update_indicator(indicator.id, {'formula': 'EMA(CLOSE, 10)'})
        print(f"   ✅ 公式更新为: {updated.formula}")
        assert updated.formula == 'EMA(CLOSE, 10)'
        
        # 测试5.4: 更新参数
        print("\n测试5.4: 更新参数")
        updated = update_indicator(indicator.id, {'parameters': {'N': 20}})
        print(f"   ✅ 参数更新")
        
        # 测试5.5: 批量更新多个字段
        print("\n测试5.5: 批量更新")
        updated = update_indicator(indicator.id, {
            'name': '最终名称',
            'description': '最终描述',
            'formula': 'RSI(CLOSE, 14)',
            'parameters': {'N': 14}
        })
        print(f"   ✅ 批量更新成功")
        assert updated.name == '最终名称'
        assert updated.formula == 'RSI(CLOSE, 14)'
        
        # 测试5.6: 更新不存在的指标
        print("\n测试5.6: 更新不存在的指标")
        try:
            update_indicator(99999, {'name': 'test'})
            print("   ❌ 应该抛出异常")
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
        # 测试5.7: 空更新数据
        print("\n测试5.7: 空更新数据")
        try:
            update_indicator(indicator.id, {})
            print("   ❌ 应该抛出异常")
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
        # 清理
        delete_indicator(indicator.id)
        print("\n   ✅ 测试数据已清理")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_delete_indicator():
    """测试删除指标"""
    print_section("测试6: 删除指标")
    
    from services.indicator_service import (
        create_indicator,
        delete_indicator,
        get_indicator
    )
    
    try:
        # 测试6.1: 删除普通指标
        print("测试6.1: 删除普通指标")
        indicator = create_indicator(name='待删除指标')
        print(f"   创建指标 ID: {indicator.id}")
        
        result = delete_indicator(indicator.id)
        print(f"   ✅ 删除结果: {result}")
        assert result == True
        
        # 验证已删除
        deleted = get_indicator(indicator.id)
        print(f"   验证删除: {deleted}")
        assert deleted is None
        
        # 测试6.2: 删除不存在的指标
        print("\n测试6.2: 删除不存在的指标")
        try:
            delete_indicator(99999)
            print("   ❌ 应该抛出异常")
        except ValueError as e:
            print(f"   ✅ 正确捕获错误: {e}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_system_indicators():
    """测试系统指标"""
    print_section("测试7: 系统指标保护")
    
    from services.indicator_service import (
        init_system_indicators,
        update_indicator,
        delete_indicator,
        get_all_indicators
    )
    
    try:
        # 初始化系统指标
        print("测试7.1: 初始化系统指标")
        created = init_system_indicators()
        print(f"   ✅ 创建/跳过系统指标")
        
        # 获取系统指标
        system_inds = get_all_indicators(is_system=True)
        print(f"   系统指标数量: {len(system_inds)}")
        
        if system_inds:
            first_system = system_inds[0]
            print(f"   第一个系统指标: {first_system.name}")
            
            # 测试7.2: 系统指标不能修改
            print("\n测试7.2: 系统指标不能修改")
            try:
                update_indicator(first_system.id, {'name': '被修改的名称'})
                print("   ❌ 应该抛出异常")
            except ValueError as e:
                print(f"   ✅ 正确阻止修改: {e}")
            
            # 测试7.3: 系统指标不能删除
            print("\n测试7.3: 系统指标不能删除")
            try:
                delete_indicator(first_system.id)
                print("   ❌ 应该抛出异常")
            except ValueError as e:
                print(f"   ✅ 正确阻止删除: {e}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise


def cleanup_all_data():
    """清理所有测试数据"""
    print("\n清理测试数据...")
    from config.database import SessionLocal
    from models.indicator import Indicator
    
    db = SessionLocal()
    try:
        # 只删除自定义指标，保留系统指标
        db.query(Indicator).filter(Indicator.is_system == 0).delete()
        db.commit()
        print("✅ 测试数据已清理")
    finally:
        db.close()


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀" * 30)
    print("开始运行 Indicator Service 测试")
    print("🚀" * 30)
    
    try:
        # 初始化数据库
        init_database()
        
        # 运行所有测试
        test_create_indicator()
        test_validate_formula()
        test_parse_parameters()
        test_get_indicators()
        test_update_indicator()
        test_delete_indicator()
        test_system_indicators()
        
        # 清理数据
        cleanup_all_data()
        
        print("\n" + "✅" * 30)
        print("所有测试通过！🎉")
        print("✅" * 30)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)