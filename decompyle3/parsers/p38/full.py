#  Copyright (c) 2017-2022 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
spark grammar differences over Python 3.7 for Python 3.8
"""

from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG
from spark_parser.spark import rule2str

from decompyle3.parsers.p37.full import Python37Parser
from decompyle3.parsers.parse_heads import ParserError
from decompyle3.parsers.p38.full_custom import Python38FullCustom
from decompyle3.parsers.p38.lambda_expr import Python38LambdaParser

from decompyle3.scanners.tok import Token


class Python38Parser(Python38LambdaParser, Python38FullCustom, Python37Parser):
    def __init__(self, start_symbol: str = "stmts", debug_parser=PARSER_DEFAULT_DEBUG):
        Python38LambdaParser.__init__(self, start_symbol, debug_parser)
        self.customized = {}

    def customize_grammar_rules(self, tokens, customize):
        self.customize_grammar_rules_full38(tokens, customize)

    ###############################################
    #  Python 3.8 grammar rules with statements
    ###############################################

    def p_38_full_walrus(self, args):
        """
        # named_expr is also known as the "walrus op" :=
        expr              ::= named_expr
        named_expr        ::= expr DUP_TOP store
        """

    def p_38_full_if_ifelse(self, args):
        """
        # cf_pt introduced to keep indices the same in ifelsestmtc
        cf_pt              ::= COME_FROM POP_TOP
        ifelsestmtc        ::= testexpr c_stmts cf_pt else_suite

        # 3.8 can push a looping JUMP_LOOP into into a JUMP_ from a statement that jumps to it
        lastc_stmt         ::= ifpoplaststmtc
        ifpoplaststmtc     ::= testexpr POP_TOP c_stmts_opt
        ifelsestmtc        ::= testexpr c_stmts_opt jb_cfs else_suitec JUMP_LOOP come_froms

        # The below ifelsetmtc is a really weird one for the inner if/else in:
        #  if a:
        #      while i:
        #       if c:
        #         j = j + 1
        #                 # A JUMP_LOOP is here...
        #       else:
        #          break
        #                 # but also a JUMP_LOOP is inserted here!
        #  else:
        #    j = 10

        ifelsestmtc        ::= testexpr c_stmts_opt JUMP_LOOP else_suitec JUMP_LOOP
        """

    def p_38_full_misc(self, args):
        """
        stmt               ::= async_for_stmt38
        stmt               ::= async_forelse_stmt38
        stmt               ::= async_with_stmt38
        stmt               ::= for38
        stmt               ::= forelselaststmt38
        stmt               ::= forelselaststmtc38
        stmt               ::= forelsestmt38
        stmt               ::= try_elsestmtl38
        stmt               ::= try_except38
        stmt               ::= try_except38r
        stmt               ::= try_except38r2
        stmt               ::= try_except38r3
        stmt               ::= try_except_as
        stmt               ::= try_except_ret38
        stmt               ::= try_except_ret38a
        stmt               ::= tryfinally38astmt
        stmt               ::= tryfinally38rstmt
        stmt               ::= tryfinally38rstmt2
        stmt               ::= tryfinally38rstmt3
        stmt               ::= tryfinally38rstmt4
        stmt               ::= tryfinally38stmt
        stmt               ::= whileTruestmt38
        stmt               ::= whilestmt38

        # FIXME: "break"" should be isolated to loops
        stmt  ::= break

        break ::= POP_BLOCK BREAK_LOOP
        break ::= POP_BLOCK POP_TOP BREAK_LOOP
        break ::= POP_TOP BREAK_LOOP
        break ::= POP_EXCEPT BREAK_LOOP
        break ::= POP_TOP CONTINUE JUMP_LOOP

        # FIXME: this should be restricted to being inside a try block
        stmt               ::= except_ret38
        stmt               ::= except_ret38a

        # FIXME: this should be added only when seeing GET_AITER or YIELD_FROM
        async_for          ::= GET_AITER _come_froms
                               SETUP_FINALLY GET_ANEXT LOAD_CONST YIELD_FROM POP_BLOCK
        async_for_stmt38   ::= expr async_for
                               store for_block
                               COME_FROM_FINALLY
                               END_ASYNC_FOR

        # FIXME: come froms after the else_suite or END_ASYNC_FOR distinguish which of
        # for / forelse is used. Add come froms and check of add up control-flow detection phase.
        async_forelse_stmt38 ::= expr async_for
                                store for_block
                                COME_FROM_FINALLY
                                END_ASYNC_FOR
                                else_suite

        async_with_stmt38    ::= LOAD_DEREF
                                 BEFORE_ASYNC_WITH
                                 GET_AWAITABLE
                                 LOAD_CONST
                                 YIELD_FROM
                                 SETUP_ASYNC_WITH
                                 POP_TOP
                                 stmts
                                 POP_BLOCK
                                 BEGIN_FINALLY
                                 COME_FROM_ASYNC_WITH
                                 WITH_CLEANUP_START
                                 GET_AWAITABLE
                                 LOAD_CONST
                                 YIELD_FROM
                                 WITH_CLEANUP_FINISH
                                 END_FINALLY

        # Seems to be used to discard values before a return in a "for" loop
        discard_top        ::= ROT_TWO POP_TOP
        discard_tops       ::= discard_top+
        pop_tops           ::= POP_TOP+

        return             ::= return_expr
                               discard_tops RETURN_VALUE

        return             ::= pop_return
        return             ::= popb_return
        return             ::= pop_ex_return
        except_stmt        ::= pop_ex_return
        pop_return         ::= POP_TOP return_expr RETURN_VALUE
        popb_return        ::= return_expr POP_BLOCK RETURN_VALUE
        pop_ex_return      ::= return_expr ROT_FOUR POP_EXCEPT RETURN_VALUE

        except_stmt        ::= except_cond1a except_suite come_from_opt

        get_iter           ::= expr GET_ITER
        for38              ::= expr get_iter store for_block JUMP_LOOP _come_froms
        for38              ::= expr get_for_iter store for_block JUMP_LOOP _come_froms
        for38              ::= expr get_for_iter store for_block JUMP_LOOP _come_froms POP_BLOCK
        for38              ::= expr get_for_iter store for_block _come_froms

        forelsestmt38      ::= expr get_for_iter store for_block POP_BLOCK else_suite
        forelsestmt38      ::= expr get_for_iter store for_block JUMP_LOOP _come_froms else_suite

        c_stmt             ::= c_forelsestmt38
        c_stmt             ::= pop_tops return
        c_forelsestmt38    ::= expr get_for_iter store for_block POP_BLOCK else_suitec
        c_forelsestmt38    ::= expr get_for_iter store for_block JUMP_LOOP _come_froms else_suitec

        # continue is a weird one. In 3.8, CONTINUE_LOOP was removed.
        # Inside an loop we can have this, which can only appear in side a try/except
        # And it can also appear at the end of the try except.
        continue           ::= POP_EXCEPT JUMP_LOOP

        forelselaststmt38  ::= expr get_for_iter store for_block POP_BLOCK else_suitec
        forelselaststmtc38 ::= expr get_for_iter store for_block POP_BLOCK else_suitec

        whilestmt38        ::= _come_froms testexpr c_stmts_opt COME_FROM JUMP_LOOP POP_BLOCK
        whilestmt38        ::= _come_froms testexpr c_stmts_opt JUMP_LOOP POP_BLOCK
        whilestmt38        ::= _come_froms testexpr c_stmts_opt JUMP_LOOP come_froms
        whilestmt38        ::= _come_froms testexpr returns               POP_BLOCK
        whilestmt38        ::= _come_froms testexpr c_stmts     JUMP_LOOP _come_froms
        whilestmt38        ::= _come_froms testexpr c_stmts     come_froms

        # while1elsestmt   ::=          c_stmts     JUMP_LOOP
        whileTruestmt      ::= _come_froms c_stmts              JUMP_LOOP _come_froms POP_BLOCK
        while1stmt         ::= _come_froms c_stmts COME_FROM_LOOP
        while1stmt         ::= _come_froms c_stmts COME_FROM JUMP_LOOP COME_FROM_LOOP
        whileTruestmt38    ::= _come_froms c_stmts JUMP_LOOP _come_froms
        whileTruestmt38    ::= _come_froms c_stmts JUMP_LOOP COME_FROM_EXCEPT_CLAUSE

        for_block          ::= _come_froms c_stmts_opt come_from_loops JUMP_LOOP

        except_cond1       ::= DUP_TOP expr COMPARE_OP POP_JUMP_IF_FALSE
                               POP_TOP POP_TOP POP_TOP
                               POP_EXCEPT
        except_cond1a      ::= DUP_TOP expr COMPARE_OP POP_JUMP_IF_FALSE
                               POP_TOP POP_TOP POP_TOP

        # except .. as var
        except_cond_as     ::= DUP_TOP expr COMPARE_OP POP_JUMP_IF_FALSE
                               POP_TOP STORE_FAST POP_TOP

        try_elsestmtl38    ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               except_handler38 COME_FROM
                               else_suitec opt_come_from_except
        try_except         ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               except_handler38
        c_try_except       ::= SETUP_FINALLY c_suite_stmts POP_BLOCK
                               except_handler38

        try_except38       ::= SETUP_FINALLY POP_BLOCK POP_TOP suite_stmts_opt
                               except_handler38a

        # suite_stmts has a return
        try_except38       ::= SETUP_FINALLY POP_BLOCK suite_stmts
                               except_handler38b
        try_except38r      ::= SETUP_FINALLY return_except
                               except_handler38b
        return_except      ::= stmts POP_BLOCK return


        # In 3.8 there seems to be some sort of code fiddle with POP_EXCEPT when there
        # is a final return in the "except" block.
        # So we treat the "return" separate from the other statements
        cond_except_stmt      ::= except_cond1 except_stmts
        cond_except_stmts_opt ::= cond_except_stmt*

        try_except38r2     ::= SETUP_FINALLY
                               suite_stmts_opt
                               POP_BLOCK JUMP_FORWARD
                               COME_FROM_FINALLY POP_TOP POP_TOP POP_TOP
                               cond_except_stmts_opt
                               POP_EXCEPT return
                               END_FINALLY
                               COME_FROM

        try_except38r3     ::= SETUP_FINALLY
                               suite_stmts_opt
                               POP_BLOCK JUMP_FORWARD
                               COME_FROM_FINALLY
                               cond_except_stmts_opt
                               POP_EXCEPT return
                               COME_FROM
                               END_FINALLY
                               COME_FROM



        try_except_as      ::= SETUP_FINALLY POP_BLOCK suite_stmts
                               except_handler_as END_FINALLY COME_FROM
        try_except_as      ::= SETUP_FINALLY suite_stmts
                               except_handler_as END_FINALLY COME_FROM


        try_except_ret38   ::= SETUP_FINALLY returns except_ret38a
        try_except_ret38a  ::= SETUP_FINALLY returns except_handler38c
                               END_FINALLY come_from_opt

        # Note: there is a suite_stmts_opt which seems
        # to be bookkeeping which is not expressed in source code
        except_ret38       ::= SETUP_FINALLY expr ROT_FOUR POP_BLOCK POP_EXCEPT
                               CALL_FINALLY RETURN_VALUE COME_FROM
                               COME_FROM_FINALLY
                               suite_stmts_opt END_FINALLY
        except_ret38a      ::= COME_FROM_FINALLY POP_TOP POP_TOP POP_TOP
                               expr ROT_FOUR
                               POP_EXCEPT RETURN_VALUE END_FINALLY

        except_handler38   ::= jump COME_FROM_FINALLY
                               except_stmts END_FINALLY opt_come_from_except
        except_handler38a  ::= COME_FROM_FINALLY POP_TOP POP_TOP POP_TOP
                               POP_EXCEPT POP_TOP stmts END_FINALLY
        except_handler38b  ::= COME_FROM_FINALLY POP_TOP POP_TOP POP_TOP
                               POP_EXCEPT returns END_FINALLY
        except_handler38c  ::= COME_FROM_FINALLY except_cond1a except_stmts
                               COME_FROM
        except_handler38c  ::= COME_FROM_FINALLY except_cond1a except_stmts
                               POP_EXCEPT JUMP_FORWARD COME_FROM

        except_handler_as  ::= COME_FROM_FINALLY except_cond_as tryfinallystmt
                               POP_EXCEPT JUMP_FORWARD COME_FROM

        except             ::= POP_TOP POP_TOP POP_TOP c_stmts_opt break POP_EXCEPT JUMP_LOOP

        # In 3.8 any POP_EXCEPT comes before the "break" loop.
        # We should add a rule to check that JUMP_FORWARD is indeed a "break".
        break              ::=  POP_EXCEPT JUMP_FORWARD
        break              ::=  POP_BLOCK POP_TOP JUMP_FORWARD

        tryfinallystmt     ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               BEGIN_FINALLY COME_FROM_FINALLY suite_stmts_opt
                               END_FINALLY


        lc_setup_finally   ::= LOAD_CONST SETUP_FINALLY
        call_finally_pt    ::= CALL_FINALLY POP_TOP
        cf_cf_finally      ::= come_from_opt COME_FROM_FINALLY
        pop_finally_pt     ::= POP_FINALLY POP_TOP
        ss_end_finally     ::= suite_stmts END_FINALLY
        sf_pb_call_returns ::= SETUP_FINALLY POP_BLOCK CALL_FINALLY returns
        sf_pb_call_returns ::= SETUP_FINALLY POP_BLOCK POP_EXCEPT CALL_FINALLY returns
        suite_stmts_return ::= suite_stmts expr
        suite_stmts_return ::= expr


        # FIXME: DRY rules below
        tryfinally38rstmt  ::= sf_pb_call_returns
                               cf_cf_finally
                               ss_end_finally
        tryfinally38rstmt  ::= sf_pb_call_returns
                               cf_cf_finally END_FINALLY
                               suite_stmts
        tryfinally38rstmt  ::= sf_pb_call_returns
                               cf_cf_finally POP_FINALLY
                               ss_end_finally
        tryfinally38rstmt  ::= sf_pb_call_returns
                               COME_FROM_FINALLY POP_FINALLY
                               ss_end_finally

        tryfinally38rstmt2 ::= lc_setup_finally POP_BLOCK call_finally_pt
                               returns
                               cf_cf_finally pop_finally_pt
                               ss_end_finally POP_TOP

        tryfinally38rstmt3 ::= SETUP_FINALLY expr POP_BLOCK CALL_FINALLY RETURN_VALUE
                               COME_FROM COME_FROM_FINALLY
                               ss_end_finally

        tryfinally38rstmt4 ::= lc_setup_finally suite_stmts_opt POP_BLOCK
                               BEGIN_FINALLY COME_FROM_FINALLY
                               suite_stmts_return
                               POP_FINALLY ROT_TWO POP_TOP
                               RETURN_VALUE
                               END_FINALLY POP_TOP


        tryfinally38stmt   ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               BEGIN_FINALLY COME_FROM_FINALLY
                               POP_FINALLY suite_stmts_opt END_FINALLY

        tryfinally38astmt  ::= LOAD_CONST SETUP_FINALLY suite_stmts_opt POP_BLOCK
                               BEGIN_FINALLY COME_FROM_FINALLY
                               POP_FINALLY POP_TOP suite_stmts_opt END_FINALLY POP_TOP
        """

    # FIXME: try this
    def reduce_is_invalid(self, rule, ast, tokens, first, last):
        lhs = rule[0]
        if lhs == "call_kw":
            # Make sure we don't derive call_kw
            nt = ast[0]
            while not isinstance(nt, Token):
                if nt[0] == "call_kw":
                    return True
                nt = nt[0]
                pass
            pass
        n = len(tokens)
        last = min(last, n - 1)
        fn = self.reduce_check_table.get(lhs, None)
        try:
            if fn:
                return fn(self, lhs, n, rule, ast, tokens, first, last)
        except:
            import sys, traceback

            print(
                f"Exception in {fn.__name__} {sys.exc_info()[1]}\n"
                + f"rule: {rule2str(rule)}\n"
                + f"offsets {tokens[first].offset} .. {tokens[last].offset}"
            )
            print(traceback.print_tb(sys.exc_info()[2], -1))
            raise ParserError(tokens[last], tokens[last].off2int(), self.debug["rules"])

        if lhs in ("aug_assign1", "aug_assign2") and ast[0][0] == "and":
            return True
        elif lhs == "annotate_tuple":
            return not isinstance(tokens[first].attr, tuple)
        elif lhs == "import_from37":
            importlist37 = ast[3]
            alias37 = importlist37[0]
            if importlist37 == "importlist37" and alias37 == "alias37":
                store = alias37[1]
                assert store == "store"
                return alias37[0].attr != store[0].attr
            return False

        return False

        return False


if __name__ == "__main__":
    # Check grammar
    from decompyle3.parsers.dump import dump_and_check

    p = Python38Parser()
    modified_tokens = set(
        """JUMP_LOOP CONTINUE RETURN_END_IF COME_FROM
           LOAD_GENEXPR LOAD_ASSERT LOAD_SETCOMP LOAD_DICTCOMP LOAD_CLASSNAME
           LAMBDA_MARKER RETURN_LAST
        """.split()
    )

    dump_and_check(p, (3, 8), modified_tokens)
