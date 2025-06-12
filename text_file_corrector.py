# -*- coding: utf-8 -*-
"""
简化版中文文本文件纠错器
专门用于处理.txt文件的批量纠错

支持的模型：
1. KenlmCorrector - 统计语言模型，速度快
2. MacBertCorrector - 深度学习模型，准确率高
3. ErnieCscCorrector - 专门针对中文拼写纠错优化
4. ConfusionCorrector - 基于混淆集的纠错
5. EnSpellCorrector - 英文拼写纠错

"""
import time
import os
import pycorrector
from pycorrector import Corrector, MacBertCorrector, ErnieCscCorrector, ConfusionCorrector, EnSpellCorrector


class TextFileCorrector:
    """文本文件纠错器"""
    
    def __init__(self, use_models=None):
        """
        初始化文本文件纠错器
        Args:
            use_models: list, 要使用的模型列表，可选：
                       ['kenlm', 'macbert', 'ernie', 'confusion', 'en_spell']
        """
        if use_models is None:
            use_models = ['kenlm', 'macbert', 'ernie', 'confusion']
        
        self.models = {}
        self.available_models = []
        
        print("正在初始化文本纠错器...")
        print("=" * 60)
        
        # 初始化各种模型
        if 'kenlm' in use_models:
            try:
                print("加载 Kenlm 模型...")
                self.models['kenlm'] = Corrector()
                self.available_models.append('kenlm')
                print("✓ Kenlm 模型加载成功")
            except Exception as e:
                print("\n")
        
        if 'macbert' in use_models:
            try:
                print("加载 MacBert 模型...")
                self.models['macbert'] = MacBertCorrector()
                self.available_models.append('macbert')
                print("✓ MacBert 模型加载成功")
            except Exception as e:
                print("\n")
        
        if 'ernie' in use_models:
            try:
                print("加载 ERNIE-CSC 模型...")
                self.models['ernie'] = ErnieCscCorrector()
                self.available_models.append('ernie')
                print("✓ ERNIE-CSC 模型加载成功")
            except Exception as e:
                print("\n")
        
        if 'confusion' in use_models:
            try:
                print("加载混淆集纠错器...")
                # 自定义混淆集，添加常见错误
                custom_confusion = {
                    # 常见拼音/语义混淆
                    "人可": "认可",
                    "那里": "哪里",
                    "在那里": "在哪里",
                    "中要": "重要",
                    "因该": "应该",
                    "天氨门": "天安门",
                    "较书": "教书",
                    "书藉": "书籍",
                    "蒙习": "学习",
                    "公理": "公里",
                    "里成": "里程",
                    "试式": "仪式",
                    "经力": "经历",
                    "生崖": "生涯",
                    "心晴": "心情",
                    "做息": "作息",
                    "息习": "学习",
                    "问提": "问题",
                    "件建": "建议",
                    "意建": "建议",
                    "发发": "发生",
                    "生发": "发生",
                    "时实": "事实",
                    "实事": "事实",
                    "认只": "认识",
                    "识知": "知识",
                    "识意": "意识",
                    "观查": "观察",
                    "细仔": "仔细",
                    "份内": "分内",
                    "分今": "身份",
                    "身分": "身份",
                    "份份": "身份",
                    "年青": "年轻",
                    "轻年": "年轻",
                    "少青": "青年",
                    "清静": "清净",
                    "净清": "清净",
                    "功克": "攻克",
                    "攻刻": "攻克",
                    "坚苦": "艰苦",
                    "苦艰": "艰苦",
                    "坚巨": "艰巨",
                    "巨坚": "艰巨",
                    "困准": "困难",
                    "难困": "困难",
                    "能愿": "愿意",
                    "原意": "愿意",
                    "原意能": "愿意",
                    "能情": "能够",
                    "能清": "能够",
                    "可能能": "能够",
                    "能会": "能够",
                    "能有": "拥有",
                    "有能": "拥有",
                    "持支": "支持",
                    "支特": "特殊",
                    "特支": "特殊",
                    "特持": "特殊",
                    "持特": "特殊",
                    "持支": "支持",
                    "持支力": "支持",
                    "支技": "技术",
                    "技支": "技术",
                    "术技": "技术",
                    "科计": "科技",
                    "技科": "科技",
                    "科技术": "科技",
                    "技创": "创新",
                    "新创": "创新",
                    "创改": "改革",
                    "革改": "改革",
                    "体机": "机制",
                    "制机": "机制",
                    "机治": "机制",
                    "质机": "机制",
                    "制度": "机制",
                    "度制": "制度",
                    "制机": "机制",
                    "机制化": "机制",
                    "机置": "机制",
                    "置机": "机制",
                    "机置定": "机制",
                    "机制定": "机制",
                    "定机": "机制",
                    "机定": "机制",
                    "机制构": "机制",
                    "机结构": "机制",
                    "构结": "结构",
                    "结机": "结构",
                    "机结": "结构",
                    "构机": "结构",
                    "机构成": "结构",
                    "构架": "架构",
                    "架构": "架构",
                    "构架设": "架构",
                    "架设构": "架构",
                    "设架": "设计",
                    "计设": "设计",
                    "设构": "设计",
                    "构设": "设计",
                    "计画": "计划",
                    "划计": "计划",
                    "计策": "计划",
                    "策划": "计划",
                    "规化": "规划",
                    "划规": "规划",
                    "规设": "规划",
                    "设规": "规划",
                    "规计": "规划",
                    "规策": "规划",
                    "策规": "规划",
                    "规布": "公布",
                    "布公": "公布",
                    "发布告": "公布",
                    "布告": "公布",
                    "公告示": "公布",
                    "示告": "告知",
                    "告示": "告知",
                    "告之": "告知",
                    "知告": "告知",
                    "告达": "传达",
                    "传大": "传达",
                    "达传": "传达",
                    "传到": "传达",
                    "到传": "传达",
                    "传述": "转述",
                    "述转": "转述",
                    "转陈": "转述",
                    "陈转": "转述",
                    "述讲": "讲述",
                    "讲诉": "讲述",
                    "讲叙": "讲述",
                    "讲术": "讲述",
                    "述说": "讲述",
                    "说述": "讲述",
                    "道述": "描述",
                    "描速": "描述",
                    "速描": "描述",
                    "绘描": "描绘",
                    "描画": "描绘",
                    "绘画": "描绘",
                    "画绘": "描绘",
                    "绘图": "图画",
                    "图绘": "图画",
                    "画图": "图画",
                    "图画画": "图画",
                    "图绘绘": "图画",
                }
                self.models['confusion'] = ConfusionCorrector(custom_confusion_path_or_dict=custom_confusion)
                self.available_models.append('confusion')
                print("✓ 混淆集纠错器加载成功")
            except Exception as e:
                print(f"✗ 混淆集纠错器加载失败: {e}")
        
        if 'en_spell' in use_models:
            try:
                print("加载英文拼写纠错器...")
                self.models['en_spell'] = EnSpellCorrector()
                self.available_models.append('en_spell')
                print("✓ 英文拼写纠错器加载成功")
            except Exception as e:
                print(f"✗ 英文拼写纠错器加载失败: {e}")
        
        print("=" * 60)
        print(f"初始化完成，可用模型：{self.available_models}")
        print(f"总共加载了 {len(self.available_models)} 个模型")
        print()
    
    def correct_single_model(self, text, model_name):
        """使用单个模型进行纠错"""
        if model_name not in self.available_models:
            return {"source": text, "target": text, "errors": [], "model": model_name, "status": "不可用"}
        
        try:
            start_time = time.time()
            result = self.models[model_name].correct(text)
            end_time = time.time()
            
            # 统一返回格式
            if isinstance(result, tuple):
                # Kenlm模型返回 (corrected_text, errors)
                return {
                    "source": text,
                    "target": result[0],
                    "errors": result[1] if result[1] else [],
                    "model": model_name,
                    "time": f"{end_time - start_time:.3f}s",
                    "status": "成功"
                }
            elif isinstance(result, dict):
                # 其他模型返回字典格式
                result.update({
                    "model": model_name,
                    "time": f"{end_time - start_time:.3f}s",
                    "status": "成功"
                })
                return result
            else:
                return {
                    "source": text,
                    "target": str(result),
                    "errors": [],
                    "model": model_name,
                    "time": f"{end_time - start_time:.3f}s",
                    "status": "成功"
                }
        except Exception as e:
            return {
                "source": text,
                "target": text,
                "errors": [],
                "model": model_name,
                "time": "0s",
                "status": f"错误: {e}"
            }
    
    def correct_text(self, text, strategy='voting'):
        """
        使用多模型集成进行纠错
        Args:
            text: 待纠错文本
            strategy: 集成策略，'voting' 或 'pipeline'
        """
        results = {}
        
        # 获取所有模型的结果
        for model_name in self.available_models:
            result = self.correct_single_model(text, model_name)
            results[model_name] = result
        
        if strategy == 'voting':
            # 投票策略：选择最常见的纠错结果
            corrections = [r['target'] for r in results.values() if r['target'] != text]
            if corrections:
                # 简单多数投票
                from collections import Counter
                vote_result = Counter(corrections).most_common(1)[0][0]
                return vote_result
            else:
                return text
        
        elif strategy == 'pipeline':
            # 流水线策略：依次应用每个模型
            current_text = text
              # 按优先级顺序应用模型
            model_order = ['kenlm', 'macbert', 'ernie', 'confusion', 'en_spell']
            
            for model_name in model_order:
                if model_name in self.available_models:
                    result = self.correct_single_model(current_text, model_name)
                    if result['target'] != current_text and result['errors']:
                        current_text = result['target']
            
            return current_text
        
        return text
    
    def correct_file(self, input_file_path, output_file_path=None, strategy='voting', encoding='utf-8', show_progress=True):
        """
        批量纠错文件内容
        Args:
            input_file_path: 输入文件路径
            output_file_path: 输出文件路径（可选，如果为None会自动生成）
            strategy: 集成策略，'voting' 或 'pipeline'
            encoding: 文件编码
            show_progress: 是否显示处理进度
        """
        # 如果没有指定输出文件路径，自动生成
        if output_file_path is None:
            import os
            base_name = os.path.splitext(input_file_path)[0]
            output_file_path = f"{base_name}_corrected.txt"
        if show_progress:
            print(f"开始处理文件: {input_file_path}")
            print(f"输出文件: {output_file_path}")
            print(f"使用策略: {strategy}")
            print("=" * 60)
        
        try:
            # 读取输入文件
            with open(input_file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
            
            corrected_lines = []
            total_lines = len(lines)
            corrected_count = 0
            
            for i, line in enumerate(lines, 1):
                original_line = line
                line = line.strip()
                
                if not line:  # 空行直接保留
                    corrected_lines.append(original_line)
                    continue
                
                if show_progress:
                    print("\n")
                
                # 使用指定策略进行纠错
                corrected_text = self.correct_text(line, strategy=strategy)
                corrected_lines.append(corrected_text + '\n')
                
                # 统计纠错数量
                if corrected_text != line:
                    corrected_count += 1
                    if show_progress:
                        print(f"  ✓ 已纠错: {corrected_text}")
                else:
                    if show_progress:
                        print("\n")
                
                if show_progress:
                    print()
            
            # 写入输出文件
            with open(output_file_path, 'w', encoding=encoding) as f:
                f.writelines(corrected_lines)
            
            if show_progress:
                print("=" * 60)
                print(f"文件处理完成！")
                print(f"输入文件: {input_file_path}")
                print(f"输出文件: {output_file_path}")
                print(f"总行数: {total_lines}")
                # print(f"纠错行数: {corrected_count}")
                print(f"使用策略: {strategy}")
            
            return {
                "success": True,
                "total_lines": total_lines,
                "corrected_lines": corrected_count,
                "correction_rate": corrected_count/total_lines*100,
                "output_file_path": output_file_path  # 返回输出文件路径
            }
            
        except FileNotFoundError:
            error_msg = f"错误: 找不到输入文件 {input_file_path}"
            if show_progress:
                print(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"处理文件时发生错误: {e}"
            if show_progress:
                print(error_msg)
                import traceback
                traceback.print_exc()
            return {"success": False, "error": error_msg}


def main():
    """主函数"""
    print("pycorrector 文本文件纠错器")
    print("=" * 60)
    
    try:
        # 创建文本纠错器
        corrector = TextFileCorrector(
            use_models=['kenlm', 'macbert', 'ernie', 'confusion', 'en_spell']
        )
        
        if not corrector.available_models:
            print("错误：没有可用的纠错模型，请检查模型安装")
            return
        
        # 文件路径配置
        input_file = "input_text.txt"  # 输入文件名
        output_file_voting = "output_voting.txt"  # 投票策略输出文件
        output_file_pipeline = "output_pipeline.txt"  # 流水线策略输出文件
        
        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            print(f"缺少输入文件")
            return 0
        
        # 使用投票策略处理文件
        print(f"\n使用投票策略处理文件...")
        result1 = corrector.correct_file(input_file, output_file_voting, strategy='voting')
        
        print(f"\n使用流水线策略处理文件...")
        result2 = corrector.correct_file(input_file, output_file_pipeline, strategy='pipeline')
        
        print(f"\n处理完成！")
        print(f"输入文件: {input_file}")
        print(f"投票策略结果: {output_file_voting}")
        print(f"流水线策略结果: {output_file_pipeline}")
        print(f"\n请查看输出文件以查看纠错结果。")
    
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n感谢使用文本文件纠错器！")


if __name__ == "__main__":
    main()

def text_file_corrector(input_file_path, strategy='voting', use_models=None, encoding='utf-8', show_progress=False):
    """
    简化的文本文件纠错接口，供外部代码调用
    
    Args:
        input_file_path: 输入文件路径
        strategy: 纠错策略，'voting' 或 'pipeline'
        use_models: 要使用的模型列表，默认使用所有可用模型
        encoding: 文件编码
        show_progress: 是否显示进度
    
    Returns:
        dict: 包含结果信息和输出文件路径的字典
        {
            "success": bool,
            "output_file_path": str,  # 纠错后的文件路径
            "total_lines": int,
            "corrected_lines": int,
            "correction_rate": float,
            "error": str  # 错误信息（如果失败）
        }
    """
    try:
        # 检查输入文件是否存在
        import os
        if not os.path.exists(input_file_path):
            return {
                "success": False,
                "error": f"输入文件不存在: {input_file_path}",
                "output_file_path": None
            }
        
        # 创建纠错器实例
        if use_models is None:
            use_models = ['kenlm', 'macbert', 'ernie', 'confusion']
        
        corrector = TextFileCorrector(use_models=use_models)
        
        if not corrector.available_models:
            return {
                "success": False,
                "error": "没有可用的纠错模型",
                "output_file_path": None
            }
        
        # 执行纠错
        result = corrector.correct_file(
            input_file_path, 
            output_file_path=None,  # 自动生成输出文件名
            strategy=strategy, 
            encoding=encoding, 
            show_progress=show_progress
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "output_file_path": None
        }
